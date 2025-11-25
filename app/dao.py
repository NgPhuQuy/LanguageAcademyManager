from app import app
from app.models import Course, Language, StudyRoute, User


def load_language():
    return Language.query.all()


def load_route():
    return StudyRoute.query.all()


def load_course(q=None, lang_id=None, route_id=None, page=None):
    query = Course.query

    if q:
        query = query.filter(Course.name.contains(q))
    if lang_id:
        query = query.filter(Course.id.__eq__(lang_id))
    if route_id:
        query = query.filter(Course.course_in_route.__eq__(route_id))
    if page:
        size = app.config['PAGE_SIZE']
        start = (int(page) - 1) * size
        query = query.slice(start, (start + size))

    return query.all()


def get_course_by_id(course_id):
    return Course.query.get(course_id)


def load_user_by_id(user_id):
    return User.query.get(user_id)
