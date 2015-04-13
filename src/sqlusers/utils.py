# -*- coding: utf-8 -*-

import uvclight
from .models import Base, Benutzer
from cromlech.browser import IPublicationRoot
from cromlech.sqlalchemy import get_session
from dolmen.sqlcontainer import SQLContainer
from ul.auth import SecurePublication
from ul.browser.decorators import with_zcml, with_i18n
from ul.sql import SQLPublication
from urllib import quote, unquote
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import implementer
from zope.location import Location, ILocation


class Site(object):

    def __init__(self, root):
        self.root = root

    def __enter__(self):
        setSite(self.root)
        return self.root

    def __exit__(self, exc_type, exc_value, traceback):
        setSite()


@implementer(IPublicationRoot)
class Container(SQLContainer):
    model = Benutzer

    def key_converter(self, id):
        keys = unquote(id)
        try:
            login, az = keys.split(' ')
            return login, az
        except ValueError:
            return None

    def key_reverse(self, obj):
        return quote('%s %s' % (obj.login, obj.az))

    def getSiteManager(self):
        return getGlobalSiteManager()


class MySQL(SQLPublication):

    def setup_database(self, engine):
        pass
    
    def site_manager(self, environ):
        root = Container(None, self.name, self.name)
        return Site(root)

    @classmethod
    def create(cls, gc, **kws):
        kws['base'] = Base
        return super(MySQL, cls).create(gc, **kws)
