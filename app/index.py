import math
from datetime import date
from flask import render_template, request, redirect, flash
from app import app, dao, login, admin, db
from app.dao import process_course_payment, count_course
from app.decorators import anonymous_required, my_login_required, enrollment_required, teacher_required
from flask_login import login_user, logout_user, current_user
import cloudinary.uploader

from app.models import Task, Course


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/user/profile")
def profile_user():
    courses = dao.get_courses_by_user(current_user.id)
    return render_template("profile.html", courses=courses)


@app.context_processor
def common_attribute():
    notifications = []
    if current_user.is_authenticated:
        notifications = dao.load_notifications(current_user.id)

    return {
        "languages": dao.load_language(),
        "levels": dao.load_level(),
        "notifications": notifications,
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
    pages = math.ceil(count_course() / app.config["PAGE_SIZE"])
    levels = dao.load_level()
    courses = dao.load_course(q=q, level_id=level_id, lang_id=lang_id,
                              price_max=price_max, price_min=price_min,
                              page=page)
    return render_template("courses.html", courses=courses, levels=levels,
                           pages=pages, page=page)


@app.route("/courses/<int:course_id>")
def course_details(course_id):
    course = dao.get_course_by_id(course_id=course_id)
    return render_template("course-details.html", course=course)


@app.route("/contact")
def my_contact():
    return render_template("contact.html")


@app.route("/login-admin", methods=["POST"])
def login_admin_process():
    username = request.form.get("username")
    password = request.form.get("password")

    user = dao.auth_user(username, password)

    if user:
        login_user(user)
        flash("Đăng nhập admin thành công!", "success")
        return redirect("/admin")
    else:
        flash("Tài khoản hoặc mật khẩu không đúng!", "danger")
        return redirect("/admin")


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


@app.route("/register", methods=["GET", "POST"])
@anonymous_required
def register_my_user():
    if request.method == "POST":
        confirm = request.form.get("confirm")
        password = request.form.get("password")

        if confirm != password:
            flash("Mật khẩu không khớp!", "danger")
            return redirect("/register")

        username = request.form.get("username")
        if dao.is_username_exist(username=username):
            flash("Username đã tồn tại!", "danger")
            return redirect("/register")

        email = request.form.get("email")
        if dao.is_email_used(email=email):
            flash("Email đã được sử dụng!", "danger")
            return redirect("/register")

        phone = request.form.get("phone")
        if dao.is_phone_used(phone=phone):
            flash("Số điện thoại này đã được đăng ký!", "danger")
            return redirect("/register")

        name = request.form.get("name")
        avatar = request.files.get("avatar")

        file_path = None
        if avatar:
            try:
                res = cloudinary.uploader.upload(avatar)
                file_path = res["secure_url"]
            except Exception:
                flash("Upload avatar thất bại!", "warning")
                return redirect("/register")

        try:
            # 1️⃣ tạo user
            user = dao.add_user(
                name=name,
                username=username,
                password=password,
                avatar=file_path,
                phone=phone,
                email=email
            )

            # 2️⃣ gán role STUDENT mặc định
            dao.add_role_to_user(user.id, "STUDENT")

            db.session.commit()

            login_user(user)
            flash("Đăng ký thành công!", "success")
            return redirect("/")

        except Exception as ex:
            db.session.rollback()
            flash("Hệ thống đang bị lỗi, vui lòng thử lại sau!", "danger")
            return redirect("/register")

    return render_template("register.html")


@app.route("/user/profile/edit", methods=["GET", "POST"])
@my_login_required
def edit_profile():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        avatar = request.files.get("avatar")

        # validate đơn giản
        if not name or not phone:
            flash("Vui lòng nhập đầy đủ thông tin", "danger")
            return redirect("/user/profile/edit")

        # upload avatar nếu có
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            current_user.avatar = res["secure_url"]

        current_user.name = name
        current_user.phone = phone

        try:
            db.session.commit()
            flash("Cập nhật hồ sơ thành công 🎉", "success")
        except:
            db.session.rollback()
            flash("Có lỗi xảy ra, vui lòng thử lại!", "danger")

        return redirect("/user/profile")

    return render_template("profile_edit.html")


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


@app.route("/my-courses/<int:course_id>")
@my_login_required
@enrollment_required
def my_course_detail(course_id):
    course = dao.get_course_by_id(course_id)
    enrollment = dao.get_enrollment(user_id=current_user.id, course_id=course_id)
    return render_template("student-course-details.html", course=course, enrollment=enrollment)


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
    course_id = request.args.get("course_id")
    courses = dao.get_courses_by_teacher(current_user.id)
    assignments = dao.get_assignments_by_course_id(course_id)
    return render_template("teacher_assignments.html", courses=courses, assignments=assignments)

@app.route("/teacher/assignments/<int:task_id>")
@my_login_required
def task_details(task_id):
    task = dao.get_task_by_id(task_id=task_id)
    submissions = dao.get_submissions_by_task(task_id)

    return render_template("task-details.html", task=task, submissions=submissions)


@app.route("/teacher/attendance")
@my_login_required
@teacher_required
def teacher_attendance():
    course_id = request.args.get("course_id")
    attend_date = request.args.get("date") or date.today().isoformat()

    classes = dao.get_classes_by_teacher(current_user.id)

    students = []
    attendance_map = {}
    course_name = None

    if course_id:
        students = dao.get_students_by_course(course_id)
        attendance_map = dao.get_attendance_map(course_id, attend_date)

        course = dao.get_course_by_id(course_id)
        course_name = course.name if course else ""

    return render_template(
        "teacher_attendance.html",
        classes=classes,
        students=students,
        attendance_map=attendance_map,
        course_id=course_id,
        course_name=course_name,
        date=attend_date
    )


@app.route("/teacher/attendance/save", methods=["POST"])
@my_login_required
@teacher_required
def save_teacher_attendance():
    course_id = request.form.get("course_id")
    attend_date = request.form.get("date")

    present_student_ids = request.form.getlist("attendance")

    dao.save_attendance(
        course_id=course_id,
        date=attend_date,
        present_student_ids=present_student_ids
    )

    flash("Lưu điểm danh thành công", "success")

    return redirect(f"/teacher/attendance?course_id={course_id}&date={attend_date}")


@app.route("/teacher/courses", methods=["GET", "POST"])
@my_login_required
@teacher_required
def teacher_grade_entry():
    courses = dao.get_courses_by_teacher(current_user.id)

    course_id = request.args.get("course_id")

    if request.method == "POST":
        course_id = request.form.get("course_id")
        enrollments = dao.get_enrollments_by_course(course_id)

        for e in enrollments:
            # ====== CỘT CỐ ĐỊNH ======
            for name in ["ATTENDANCE", "MIDTERM", "FINAL"]:
                key = f"{name.lower()}_{e.id}"
                value = request.form.get(key)

                if value not in [None, ""]:
                    dao.save_score(
                        enrollment_id=e.id,
                        name=name,
                        score=float(value)
                    )

            # ====== CỘT ĐIỂM ĐỘNG ======
            for form_key, value in request.form.items():
                if form_key.startswith("extra_") and value not in ["", None]:
                    _, idx, enrollment_id = form_key.split("_")

                    if int(enrollment_id) == e.id:
                        dao.save_score(
                            enrollment_id=e.id,
                            name=f"EXTRA_{idx}",
                            score=float(value),
                            rate=0.1  # hoặc tùy bạn
                        )

        flash("✅ Đã lưu toàn bộ bảng điểm", "success")

    # ====== LOAD LẠI DATA ======
    enrollments = []
    kw = request.args.get("kw")

    if course_id:
        enrollments = dao.get_enrollments_by_course(course_id)
        if kw:
            enrollments = [
                e for e in enrollments
                if kw.lower() in e.user.name.lower()
            ]

    return render_template(
        "teacher_grade_entry.html",
        courses=courses,
        enrollments=enrollments,
        selected_course_id=course_id,
        kw=kw
    )


@app.route("/statistics")
@my_login_required
def statistics_page():
    return render_template("statistics.html")


@app.route("/invoices")
@my_login_required
def invoices_page():
    return render_template("invoices.html")


@app.route("/teacher/assignments/create", methods=["GET", "POST"])
@my_login_required
def create_task():
    course_id = request.args.get("course_id", type=int)

    if request.method == "POST":
        task = Task(
            name=request.form.get("name"),
            description=request.form.get("description"),
            deadline=request.form.get("deadline"),
            course_id=request.form.get("course_id")
        )
        db.session.add(task)
        db.session.commit()
        return redirect(f"/teacher/assignments?course_id={course_id}")

    return render_template(
        "teacher-assignment-create.html",
        courses=Course.query.all(),
        selected_course_id=course_id,
        task=None
    )


if __name__ == "__main__":
    app.run(debug=True)
