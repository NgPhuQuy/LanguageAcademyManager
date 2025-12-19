from flask import render_template, request, redirect
from app import app, dao, login, admin, db
from app.decorators import anonymous_required
from flask_login import login_user, logout_user, current_user, login_required
import cloudinary.uploader


@app.route("/")
def index():
    levels = dao.load_level()
    return render_template("index.html", levels=levels)


@app.route("/user/profile/<int:user_id>")
def profile_user(user_id):
    user = dao.get_user_by_id(user_id=user_id)
    return render_template("profile.html", user=user)


@app.route("/topup")
@login_required
def top_up_my_user():
    return render_template("topup.html")


@app.route("/courses")
@app.route("/courses/level/<int:level_id>")
def my_courses(level_id=None, lang_id=None):
    q = request.args.get("q")
    langs = dao.load_language()
    levels = dao.load_level()
    courses = dao.load_course(q=q, level_id=level_id, lang_id=lang_id)
    return render_template("courses.html", courses=courses,languages=langs, levels=levels)


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
            return redirect("/")  # ERROR!!!!

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


@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect("/")


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == "__main__":
    app.run(debug=True)
