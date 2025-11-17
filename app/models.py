from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from enum import Enum as RoleEnum
from app import db, app
from datetime import datetime, timezone


class UserRole(RoleEnum):
    ADMIN = 1
    STUDENT = 2
    TEACHER = 3
    CASHIER = 4


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    def __str__(self):
        return self.name

class Fee(Base):
    fee = Column(Integer)
    course = relationship('Course', backref="Fee", lazy=True)

class Score(Base):
    score = Column(Float)
    enrollment = relationship('Enrollment', backref="Score", lazy=True)


class User(Base):
    # __abstract__ = True
    account = relationship('Account', backref="User", lazy=True)
    email = Column(String(255), nullable=False)


class Account(UserMixin, Base):
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)


class Language(Base):
    course = relationship('Course', backref="Language", lazy=True)


class Student(User):
    enrollment = relationship('Enrollment', backref="Student", lazy=True)


class Course(Base):
    lang_id = Column(Integer, ForeignKey(Language.id), nullable=False)
    enrollment = relationship('Enrollment', backref="Course", lazy=True)
    fee = Column(Integer, ForeignKey(Fee.id), nullable=False)


class Enrollment(Base):
    student_id = Column(Integer, ForeignKey(Student.id), primary_key=True)
    course_id = Column(Integer, ForeignKey(Course.id), primary_key=True)
    date = Column(DateTime, default=datetime.now(timezone.utc))
    score_id = Column(Integer, ForeignKey(Score.id), nullable=False)


class Teacher(User):
    myClass = relationship('MyClass', backref="Teacher", lazy=True)


class Cashier(User):
    bill = relationship('Bill', backref="Cashier", lazy=True)


class Bill(Base):
    cashier_id = Column(Integer, ForeignKey(Cashier.id), nullable=False)


class MyClass(Base):
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)


if __name__=="__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()