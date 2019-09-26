# -*- coding: utf-8 -*-

import uvclight

from os import path
from cromlech.browser import IPublicationRoot
from cromlech.sessions.jwt import JWTCookieSession
from cromlech.sessions.jwt import key_from_file
from dolmen.sqlcontainer import SQLContainer
from grokcore.security import Permission
from siguvtheme.uvclight import IDGUVRequest
from ul.auth import SecurePublication, ICredentials, GenericSecurityPolicy
from ul.auth import unauthenticated_principal
from ul.browser.decorators import with_zcml, with_i18n
from ul.sql import SQLPublication
from urllib import quote, unquote
from uvc.themes.btwidgets import IBootstrapRequest
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import implementer
from zope.location import Location
from zope.security.management import setSecurityPolicy
from cromlech.sqlalchemy import get_session

from .models import Base, Admin, Benutzer, Department


class ManageUsers(Permission):
    uvclight.name('manage.users')
    uvclight.title('Manage users')


class ManageDepartments(Permission):
    uvclight.name('manage.departments')
    uvclight.title('Manage departments')


class Site(object):

    def __init__(self, root):
        self.root = root

    def __enter__(self):
        setSite(self.root)
        return self.root

    def __exit__(self, exc_type, exc_value, traceback):
        setSite()


class UsersContainer(SQLContainer):
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

    @property
    def session(self):
        return get_session('sqlusers') 


class AdminsContainer(SQLContainer):
    model = Admin

    def key_reverse(self, obj):
        return obj.login

    def key_converter(self, id):
        return unquote(id)

    @property
    def session(self):
        return get_session('sqlusers') 


class DepartmentsContainer(SQLContainer):
    model = Department

    def key_converter(self, id):
        return unquote(id)

    def key_reverse(self, obj):
        return quote(obj.id)

    @property
    def session(self):
        return get_session('sqlusers') 


Users = UsersContainer(None, parent=None, name='users')
Admins = AdminsContainer(None, parent=None, name="admins")
Departments = DepartmentsContainer(None, parent=None, name='departments')


ADMINS = {
    'admin': 'admin',
    'administrator': 'guvv10',
    'freygu': 'guvv10',
}


class AdminCredentials(uvclight.GlobalUtility):
    uvclight.name('admin')
    uvclight.implements(ICredentials)

    def log_in(self, request, username, password, **data):
        if username in ADMINS.keys():
            return password == ADMINS[username]
        else:
            try:
                user = Admins[username]
                return user is not None and user.password == password
            except KeyError:
                return False


@implementer(IPublicationRoot)
class MySQL(Location, SQLPublication, SecurePublication):
    uvclight.traversable('admins', 'users', 'departments')
    layers = [IDGUVRequest, IBootstrapRequest]
    credentials = ['admin']

    @property
    def users(self):
        Users.__parent__ = self
        return Users

    @property
    def admins(self):
        Admins.__parent__ = self
        return Admins

    @property
    def departments(self):
        Departments.__parent__ = self
        return Departments

    def getSiteManager(self):
        return getGlobalSiteManager()

    def setup_database(self, engine):
        pass

    def site_manager(self, environ):
        return Site(self)

    def principal_factory(self, username):
        principal = SecurePublication.principal_factory(self, username)
        if principal is not unauthenticated_principal:
            if username not in ADMINS.keys():
                account = Admins[username]
                principal.permissions = set(('zope.View', 'manage.users',))
                principal.department = account.department_id
            else:
                principal.permissions = set(
                    ('zope.View', 'manage.users', 'manage.departments'))
            principal.roles = set()
        return principal

    @classmethod
    def create(cls, gc, **kws):
        kws['base'] = Base
        setSecurityPolicy(GenericSecurityPolicy)
        session_key = kws.get("session_key", "session")
        key = key_from_file(path.join(kws.pop('root'), 'jwt.key'))
        session_wrapper = JWTCookieSession(key, 60, environ_key=session_key)
        app = super(MySQL, cls).create(gc, **kws)
        return session_wrapper(app.__call__)
