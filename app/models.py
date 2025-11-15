from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from enum import Enum as RoleEnum
from app import db


class UserRole(RoleEnum):
    ADMIN = 1
    STUDENT = 2
    TEACHER = 3
    CASHIER = 4


class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)


class User(Base):
    account = relationship('Account', backref="User", lazy=True)
    email = Column(String(255), nullable=False, )


class Account(UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)


class Student(User):
    pass


class Teacher(User):
    myClass = relationship('MyClass', backref="Teacher", lazy=True)


class Cashier(User):
    bill = relationship('Bill', backref="Cashier", lazy=True)


class Language(Base):
    course = relationship('Course', backref="Language", lazy=True)


class Bill(Base):
    cashier_id = Column(Integer, ForeignKey(Cashier.id), nullable=False)


class Course(Base):
    lang_id = Column(Integer, ForeignKey(Language.id), nullable=False)


class MyClass(Base):
    teacher_id = Column(Integer, ForeignKey(Teacher.id), nullable=False)


class Fee(Base):
    fee = Column(Integer)


class Score(Base):
    score = Column(Integer)
