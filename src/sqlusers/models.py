# -*- coding: utf-8 -*-

from .interfaces import IBenutzer, IDepartment, IUser
from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from zope.interface import implementer


Base = declarative_base()


@implementer(IDepartment)
class Department(Base):
    __tablename__ = "department"

    id = Column(String(50), primary_key=True)
    title = Column(String(50))


@implementer(IUser)
class Admin(Base):
    __tablename__ = "admin"

    login = Column(String(20), primary_key=True)
    password = Column(String(10))
    email = Column(String(50))
    department_id = Column(String(50), ForeignKey(Department.id))

    department = relationship(
        "Department",
        uselist=False,
        backref="admlin")


@implementer(IBenutzer)
class Benutzer(Base):
    __tablename__ = "benutzer"

    login = Column(String(20), primary_key=True)
    az = Column(String(3), primary_key=True)
    password = Column(String(10))

    email = Column(String(50))
    name1 = Column(String(50))
    name2 = Column(String(50))
    name3 = Column(String(50))
    strasse = Column(String(50))
    nr = Column(String(50))
    plz = Column(String(7))
    ort = Column(String(50))
    oid = Column(String(20))
    merkmal = Column(String(10))

    department_id = Column(String(50), ForeignKey(Department.id))

    department = relationship(
        "Department",
        uselist=False,
        backref="users")
