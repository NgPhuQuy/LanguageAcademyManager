from app import app, db
from app.models import Course, Language, User, Level, Notification, Enrollment
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


def add_user(name, username, password, avatar, phone):
    password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
    u = User(name=name, username=username.strip(), password=password, avatar=avatar, phone=phone)
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
    user.money -= course.fee
    enrollment = Enrollment(user=user, course=course)
    db.session.add(enrollment)
    db.session.commit()
    return True


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


if __name__ == "__main__":
    with app.app_context():
        print(load_notifications(1))
