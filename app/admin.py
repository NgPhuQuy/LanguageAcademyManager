from flask import redirect
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from sqlalchemy import func
from app import app, db
from app.models import User, Role, UserRole, Language, Course, Enrollment, Notification, Bill
from wtforms import TextAreaField
from wtforms.widgets import TextArea


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("class", "ckeditor")
        return super().__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class MyAuthenticatedView(ModelView):
    def is_accessible(self) -> bool:
        return (
                current_user.is_authenticated
                and current_user.has_role("ADMIN")
        )

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/login")


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        # KPI
        total_users = db.session.query(User).count()
        total_courses = db.session.query(Course).count()
        total_enrollments = db.session.query(Enrollment).count()
        unread_notifications = db.session.query(Notification) \
            .filter(Notification.is_read == False).count()

        # Chart 1: Courses per language
        cate_stats = db.session.query(
            Language.id,
            Language.name,
            func.count(Course.id)
        ).join(Course, Course.lang_id == Language.id) \
            .group_by(Language.id).all()

        # Chart 2: Top 5 courses by enrollment
        course_stats = db.session.query(
            Course.name,
            func.count(Enrollment.id)
        ).join(Enrollment, Enrollment.course_id == Course.id) \
            .group_by(Course.id) \
            .order_by(func.count(Enrollment.id).desc()) \
            .limit(5).all()

        # Latest notifications
        latest_notifications = db.session.query(Notification) \
            .order_by(Notification.created_at.desc()) \
            .limit(6).all()

        return self.render(
            "admin/index.html",
            total_users=total_users,
            total_courses=total_courses,
            total_enrollments=total_enrollments,
            unread_notifications=unread_notifications,
            cate_stats=cate_stats,
            course_stats=course_stats,
            latest_notifications=latest_notifications
        )


class MyLogoutView(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")

    def is_accessible(self):
        return current_user.is_authenticated


class UserAdmin(MyAuthenticatedView):
    column_list = (
        "id", "name", "username",
        "email", "phone", "status", "money"
    )
    column_searchable_list = ("username", "email", "phone")
    column_filters = ("status",)

    can_delete = False
    form_excluded_columns = (
        "password", "enrollment",
        "bill", "teach",
        "notifications", "user_role"
    )


class RoleAdmin(MyAuthenticatedView):
    column_list = ("id", "name", "description")
    column_searchable_list = ("name",)


class UserRoleAdmin(MyAuthenticatedView):
    column_list = ("user_id", "role_id")


class LanguageAdmin(MyAuthenticatedView):
    column_list = ("id", "name")
    column_searchable_list = ("name",)


class CourseAdmin(MyAuthenticatedView):
    column_list = (
        "name", "fee",
        "language", "level",
        "teacher"
    )
    column_searchable_list = ("name",)
    column_filters = ("language", "level")

    can_export = True
    extra_js = ["//cdn.ckeditor.com/4.6.0/standard/ckeditor.js"]
    form_overrides = {
        "description": CKTextAreaField
    }


class EnrollmentAdmin(MyAuthenticatedView):
    column_list = (
        "id", "user",
        "course", "status",
        "day_assignment"
    )
    column_filters = ("status",)


class BillAdmin(MyAuthenticatedView):
    column_list = ("id", "user", "id_cashier")


class NotificationAdmin(MyAuthenticatedView):
    column_list = (
        "id", "name",
        "user", "course",
        "is_read", "created_at"
    )
    column_filters = ("is_read",)


admin = Admin(app, name="Language Academy Manager", index_view=MyAdminIndexView())

admin.add_view(UserAdmin(User, db.session, name="Users"))
admin.add_view(RoleAdmin(Role, db.session, name="Roles"))
admin.add_view(UserRoleAdmin(UserRole, db.session, name="User Roles"))
admin.add_view(LanguageAdmin(Language, db.session, name="Languages"))
admin.add_view(CourseAdmin(Course, db.session, name="Courses"))
admin.add_view(EnrollmentAdmin(Enrollment, db.session, name="Enrollments"))
admin.add_view(BillAdmin(Bill, db.session, name="Bills"))
admin.add_view(NotificationAdmin(Notification, db.session, name="Notifications"))
admin.add_view(MyLogoutView(name="Đăng xuất"))
