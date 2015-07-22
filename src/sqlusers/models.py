# -*- coding: utf-8 -*-

from .interfaces import IBenutzer, IDepartement
from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from zope.interface import implementer


Base = declarative_base()


membership_table = Table('membership', Base.metadata,
    Column('login', Integer, ForeignKey('benutzer.login')),
    Column('department', Integer, ForeignKey('department.id'))
)


@implementer(IBenutzer)
class Benutzer(Base):
    __tablename__ = "benutzer"

    login = Column(String(20), primary_key=True)
    az = Column(String(3), primary_key=True)
    password = Column(String(10))
    roles = Column(Text)
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

    departments = relationship(
        "membership",
        secondary=membership_table,
        backref="users")


@implementer(IDepartement)
class Department(Base):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), primary_key=True)
