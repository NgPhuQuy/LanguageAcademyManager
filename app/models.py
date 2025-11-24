from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from enum import Enum as RoleEnum
from app import db, app
from datetime import datetime


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    def __str__(self):
        return self.name


class User(Base, UserMixin):
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    avatar = Column(String(300), default="")
    status = Column(Boolean, default=True)

    enrollment = relationship('enrollment', backref="user", lazy=True)
    user_role = relationship('userRole', backref='user', lazy=True)
    bill = relationship('bill', backref='user', lazy=True)


class Role(Base):
    user_role = relationship('userRole', backref='role', lazy=True)


class UserRole(Base):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    role_id = Column(Integer, ForeignKey(Role.id), nullable=False)


class Language(Base):
    course = relationship('course', backref='language', lazy=True)


class StudyRoute(Base):
    course_in_route = relationship('courseInRoute', backref='studyRoute', lazy=True)


class Course(Base):
    lang_id = Column(Integer, ForeignKey(Language.id), nullable=False)

    enrollment = relationship('enrollment', backref='course', lazy=True)
    course_in_route = relationship('courseInRoute', backref='course', lazy=True)


class CourseInRoute(Base):
    id_route = Column(Integer, ForeignKey(StudyRoute.id), nullable=False)
    id_course = Column(Integer, ForeignKey(Course.id), nullable=False)


class Enrollment(Base):
    id_user = Column(Integer, ForeignKey(User.id), nullable=False)
    id_course = Column(Integer, ForeignKey(Course.id), nullable=False)
    day_assignment = Column(DateTime, default=datetime.now())
    score = relationship('score', backref='enrollment', lazy=True)


class Score(Base):
    score = Column(Float, default=0.0)
    rate = Column(Float, default=0.0)
    enrollment_id = Column(Integer, ForeignKey(Enrollment.id), nullable=False)


class Bill(Base):
    id_cashier = Column(Integer, ForeignKey(User.id), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()
