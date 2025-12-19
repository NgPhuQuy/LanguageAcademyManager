from flask import redirect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from app import app, db, dao
from app.models import User, Language, Course
from flask_admin import BaseView
from flask_login import logout_user, current_user
from wtforms import TextAreaField
from wtforms.widgets import TextArea

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class MyAuthenticatedView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.has_role(role_name="ADMIN")

class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('admin/index.html')

class MyLogoutView(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")

    def is_accessible(self) -> bool:
        return current_user.is_authenticated


class MyLanguageView(MyAuthenticatedView):
    column_list = ["id", "name"]
    column_searchable_list = ["name"]
    column_filters = ["name"]

class MyCourseView(MyAuthenticatedView):
    column_list = ['name', 'fee', 'image', 'language', 'description']
    column_searchable_list = ["name"]
    column_filters = ["language", "name"]
    column_labels = {
        "name": "Tên Khóa học",
        "fee": "Học phí"
    }
    can_export = True
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'description': CKTextAreaField
    }


admin = Admin(
    app=app,
    name="Language Academy Manager",
    index_view=MyAdminIndexView()
)


admin.add_view(MyCourseView(Course, db.session))
admin.add_view(MyLanguageView(Language, db.session))
admin.add_view(MyLogoutView("Đăng xuất"))
