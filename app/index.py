import math
from flask import render_template, request, redirect, flash
from app import app, dao, login, admin, db
from app.dao import process_course_payment
from app.decorators import anonymous_required, my_login_required
from flask_login import login_user, logout_user, current_user
import cloudinary.uploader


@app.route("/")
def index():
    levels = dao.load_level()
    return render_template("index.html", levels=levels)


@app.route("/user/profile")
def profile_user():
    return render_template("profile.html")


@app.context_processor
def common_attribute():
    return {
        "languages": dao.load_language(),
        "levels": dao.load_level(),
        "notifications":dao.load_notifications(current_user.id)
    }

@app.route("/topup")
@my_login_required
def top_up_my_user():
    return render_template("topup.html")


@app.route("/courses")
@app.route("/courses/level/<int:level_id>")
def my_courses(level_id=None, lang_id=None):
    price_min = int(request.args.get("priceMin", 0))
    price_max = int(request.args.get("priceMax", 5_000_000))
    q = request.args.get("q")
    page = request.args.get("page", 1, type=int)
    pages = math.ceil(dao.count_course() / app.config["PAGE_SIZE"])
    levels = dao.load_level()
    courses = dao.load_course(q=q, level_id=level_id, lang_id=lang_id,
                              price_max=price_max, price_min=price_min,
                              page=page)
    return render_template("courses.html", courses=courses, levels=levels,
                           pages=pages, page=page)


@app.route("/courses/<int:course_id>")
def course_details(course_id):
    course = dao.get_course_by_id(course_id= course_id)
    return render_template("course-details.html", course=course)


@app.route("/contact")
def my_contact():
    return render_template("contact.html")


@app.route("/test")
def my_test():
    return render_template("test.html")


# @app.route("/login-admin", methods=["post"])
# def login_admin_process():
#     username = request.form.get("username")
#     password = request.form.get("password")
#
#     user = dao.auth_user(username, password)
#
#     if user:
#         login_user(user)
#
#     else:
#         err_msg = "Tài khoản hoặc mật khẩu không đúng!"
#
#     return redirect("/admin")


@app.route("/login", methods=["get", "post"])
@anonymous_required
def login_my_user():
    err_msg = None
    if request.method.__eq__("POST"):
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.auth_user(username=username, password=password)

        if user:
            login_user(user)
            return redirect("/")

        else:
            err_msg = "Tài khoản hoặc mật khẩu không đúng!!"

    return render_template("login.html", err_msg=err_msg)


@app.route("/register", methods=["get", "post"])
@anonymous_required
def register_my_user():
    err_msg = None

    if request.method.__eq__("POST"):
        confirm = request.form.get("confirm")
        password = request.form.get("password")

        if confirm != password:
            err_msg = "Mật khẩu không khớp!!!"
            return render_template("register.html", err_msg=err_msg)

        username = request.form.get("username")
        if dao.is_username_exist(username=username):
            err_msg = "username đã tồn tại!"
            return render_template("register.html", err_msg=err_msg)

        phone = request.form.get("phone")
        if dao.is_phone_used(phone=phone):
            err_msg = "Số điện thoại này đã được đăng ký!"
            return render_template("register.html", err_msg=err_msg)

        else:
            name = request.form.get("name")
            avatar = request.files.get("avatar")

            file_path = None
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                file_path = res['secure_url']
            try:
                login_user(dao.add_user(name=name, username=username, password=password, avatar=file_path,phone=phone))
                return redirect('/')
            except:
                db.session.rollback()
                err_msg = "Hệ thống đang bị lỗi! xin vui lòng quay lại sau."

    return render_template("register.html", err_msg=err_msg)

@app.route("/notifications")
@my_login_required
def notifications_page():
    return render_template("notifications.html")



@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect("/")


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/student")
@my_login_required
def student_page():
    return render_template("student.html")


@app.route("/my-courses/<int:course_id>")
def user_course_detail(course_id):
    course = dao.get_course_by_id(course_id=course_id)
    return render_template("student_course_details.html", course=course)

@app.route("/my-courses")
def user_course():
    courses = dao.get_courses_by_user(user_id=current_user.id)
    return render_template("student_course.html", courses=courses)

@app.route("/courses/<int:course_id>/payment", methods=["GET", "POST"])
@my_login_required
def course_payment(course_id):

    course = dao.get_course_by_id(course_id=course_id)
    if not course:
        flash("Khóa học không tồn tại!", "danger")
        return redirect("/courses")


    current_students = dao.count_course_students(course_id)
    if current_students >= app.config["MAX_STUDENTS_PER_COURSE"]:
        flash("Lớp học đã đủ 25 học viên!!", "danger")
        return redirect("/courses")


    if dao.is_user_enrolled(current_user.id, course_id):
        flash("Bạn đã đăng ký khóa học này rồi!", "warning")
        return redirect("/my-courses/" + str(course_id))


    if request.method == "POST":
        if current_user.money < course.fee:
            flash("Số dư không đủ để thanh toán khóa học này", "danger")
            return redirect("/courses/" + str(course_id) + "/payment")

        process_course_payment(user=current_user, course=course)

        flash("Thanh toán thành công !!!", "success")
        return redirect("/my-courses/" + str(course_id))

    return render_template("payment.html", course=course, current_students=current_students,
                           max_students=app.config["MAX_STUDENTS_PER_COURSE"])



@app.route("/teacher/assignments")
@my_login_required
def teacher_assignments():
    return render_template("teacher_assignments.html")


@app.route("/teacher_attendance")
@my_login_required
def teacher_attendance():
    return render_template("teacher_attendance.html")


@app.route("/teacher_grade_entry")
@my_login_required
def teacher_grade_entry():
    return render_template("teacher_grade_entry.html")


@app.route("/statistics")
@my_login_required
def statistics_page():
    return render_template("statistics.html")


@app.route("/invoices")
@my_login_required
def invoices_page():
    return render_template("invoices.html")


if __name__ == "__main__":
    app.run(debug=True)
