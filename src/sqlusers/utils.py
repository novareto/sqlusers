# -*- coding: utf-8 -*-

import uvclight
from .models import Base, Benutzer
from cromlech.browser import IPublicationRoot
from dolmen.sqlcontainer import SQLContainer
from grokcore.security import Permission
from siguvtheme.uvclight import IDGUVRequest
from ul.auth import SecurePublication, ICredentials, GenericSecurityPolicy
from ul.browser.decorators import with_zcml, with_i18n
from ul.sql import SQLPublication
from urllib import quote, unquote
from uvc.themes.btwidgets import IBootstrapRequest
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import implementer
from zope.security.management import setSecurityPolicy


class ManageUsers(Permission):
    uvclight.name('manage.users')
    uvclight.title('Manage users')


class Site(object):

    def __init__(self, root):
        self.root = root

    def __enter__(self):
        setSite(self.root)
        return self.root

    def __exit__(self, exc_type, exc_value, traceback):
        setSite()


class MyCredentials(uvclight.GlobalUtility):
    uvclight.name('admin_only')
    uvclight.implements(ICredentials)

    def log_in(self, **data):
        return data['username'] == 'admin' and data['password'] == 'admin'


@implementer(IPublicationRoot)
class Container(SQLContainer):
    model = Benutzer
    credentials = ['admin_only']

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


class MySQL(SQLPublication, SecurePublication):
    layers = [IDGUVRequest, IBootstrapRequest]
    
    def setup_database(self, engine):
        pass

    def site_manager(self, environ):
        root = Container(None, self.name, self.name)
        return Site(root)

    def principal_factory(self, username):
        principal = SecurePublication.principal_factory(self, username)
        if username == 'admin':
            principal.permissions.add('manage.users')
        return principal

    @classmethod
    def create(cls, gc, **kws):
        kws['base'] = Base
        setSecurityPolicy(GenericSecurityPolicy)
        return super(MySQL, cls).create(gc, **kws)
