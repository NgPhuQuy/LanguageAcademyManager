from app import app, db
from app.models import Course, Language, User, Level, Notification, Enrollment, Role, UserRole, Score, Attendance
import hashlib


def load_language():
    return Language.query.all()


def load_level():
    return Level.query.all()


def get_level(level_id):
    return Level.query.filter(Level.id.__eq__(level_id))


def load_course(q=None, lang_id=None, page=None, level_id=None, price_min=0, price_max=5000000):
    query = Course.query.filter(Course.fee.between(price_min, price_max))

    if q:
        query = query.filter(Course.name.contains(q))
    if lang_id:
        query = query.filter(Course.lang_id.__eq__(lang_id))
    if level_id:
        query = query.filter(Course.level_id.__eq__(level_id))

    if page:
        size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * size
        query = query.slice(start, (start + size))

    return query.all()


def get_course_by_id(course_id):
    return Course.query.get(course_id)


def auth_user(username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username.__eq__(username), User.password.__eq__(password)).first()


def add_user(name, username, password, avatar, phone, email):
    password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
    u = User(name=name, username=username.strip(), password=password, avatar=avatar, phone=phone, email=email)
    db.session.add(u)
    db.session.commit()
    return u


def get_user_by_id(user_id):
    return User.query.get(user_id)


def is_username_exist(username):
    return db.session.query(User.id) \
        .filter(User.username == username) \
        .first() is not None


def is_phone_used(phone):
    return db.session.query(User.id) \
        .filter(User.phone == phone) \
        .first() is not None


def count_course():
    return Course.query.count()


def load_notifications(user_id):
    return Notification.query.filter(Notification.user_id.__eq__(user_id))


def is_user_enrolled(user_id, course_id):
    return Enrollment.query.filter(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id
    ).first() is not None


def process_course_payment(user, course):
    try:
        user.money -= course.fee

        enrollment = Enrollment(
            user_id=user.id,
            course_id=course.id,
            status=True
        )
        db.session.add(enrollment)
        db.session.flush()

        scores = [
            Score(score=0, rate=0.1, enrollment_id=enrollment.id),  # chuyên cần
            Score(score=0, rate=0.3, enrollment_id=enrollment.id),  # giữa kỳ
            Score(score=0, rate=0.6, enrollment_id=enrollment.id)  # cuối kỳ
        ]
        db.session.add_all(scores)

        db.session.commit()
        return True

    except Exception as ex:
        db.session.rollback()
        print("PAYMENT ERROR:", ex)
        return False


def count_course_students(course_id):
    return (db.session.query(Enrollment)
            .filter(Enrollment.course_id == course_id)
            .count())


def get_courses_by_user(user_id):
    return ((Course.query.join(Enrollment, Enrollment.course_id == Course.id)
             .filter(Enrollment.user_id == user_id))
            .all())


def get_enrollment(user_id, course_id):
    return Enrollment.query.filter(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id).first()


def is_email_used(email):
    return (db.session.query(User.id).
            filter(User.email == email).
            first() is not None)


def add_role_to_user(user_id, role_name):
    role = db.session.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise Exception("Role không tồn tại")

    ur = UserRole(user_id=user_id, role_id=role.id)
    db.session.add(ur)


def get_classes_by_teacher(teacher_id):
    return db.session.query(Course).filter(Course.teacher_id == teacher_id).all()


def get_students_by_course(course_id):
    students = (db.session.query(User).join(Enrollment, Enrollment.user_id == User.id)
                .filter(Enrollment.course_id == course_id, Enrollment.status == True).order_by(User.name.asc()).all())
    return students
def save_attendance(course_id, date, present_student_ids):
    enrollments = (db.session.query(Enrollment)
                   .filter(
                       Enrollment.course_id == course_id,
                       Enrollment.status == True
                   ).all())

    for e in enrollments:
        attendance = Attendance.query.filter_by(
            enrollment_id=e.id,
            attend_date=date
        ).first()

        if not attendance:
            attendance = Attendance(
                enrollment_id=e.id,
                attend_date=date
            )
            db.session.add(attendance)

        attendance.present = str(e.user_id) in present_student_ids

    db.session.commit()



def get_attendance_map(course_id, attend_date):
    rows = (db.session.query(Attendance)
            .join(Enrollment)
            .filter(
                Enrollment.course_id == course_id,
                Attendance.attend_date == attend_date
            ).all())

    return {a.enrollment.user_id: a.present for a in rows}
