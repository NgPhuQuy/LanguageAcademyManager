from app import app, db
from app.models import Course, Language, User, Level, Goal
import hashlib


def load_language():
    return Language.query.all()

def load_level():
    return Level.query.all()

def get_level(level_id):
    return Level.query.filter(Level.id.__eq__(level_id))

def load_course(q=None, lang_id=None, page=None, level_id=None):
    query = Course.query

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
    return db.session.query(User.id)\
        .filter(User.username == username)\
        .first() is not None

def is_phone_used(phone):
    return db.session.query(User.id)\
        .filter(User.phone == phone)\
        .first() is not None

if __name__=="__main__":
    with app.app_context():
        print(is_phone_used("0909123453"))
        # for i in load_level():
        #     print(i.)
        # print(load_level())