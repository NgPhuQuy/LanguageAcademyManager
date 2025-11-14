from sqlalchemy import Column, Integer, String, Enum
from flask_login import UserMixin
from enum import Enum as RoleEnum

from app import db

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name=Column(String(255), nullable=False)


class UserRole(RoleEnum):
    ADMIN = 1
    STUDENT = 2
    TEACHER = 3
    CASHIER = 4


# class Student(Base):
#     abc =Column()
#
# class Teacher(Base):
#     abc = Column()
#
# class Cashier(Base):
#     abc = Column()

class User(Base, UserMixin):
    username = Column()
    password = Column()
    role = Column(Enum(UserRole), default=UserRole.STUDENT)


class Language(Base):


class Bill():

class Course(Base):