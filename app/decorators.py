from functools import wraps
from flask import redirect, flash
from flask_login import current_user

from app import dao


def anonymous_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated_func


def my_login_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated_func


def enrollment_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        course_id = kwargs.get("course_id")
        if not dao.is_user_enrolled(current_user.id, course_id):
            flash("Bạn chưa đăng ký khóa học này!", "danger")
            return redirect("/courses")
        return f(*args, **kwargs)

    return decorated_func


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.has_role("TEACHER"):
            flash("Bạn không có quyền truy cập trang này!!!", "danger")
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function
