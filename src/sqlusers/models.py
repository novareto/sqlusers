# -*- coding: utf-8 -*-

from .interfaces import IBenutzer
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from zope.interface import implementer


Base = declarative_base()


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
    mysql_engine='InnoDB'
