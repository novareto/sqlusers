# -*- coding: utf-8 -*-

import uvclight
from ..interfaces import IUser, IBenutzer, IDepartment
from ..models import Benutzer, Admin
from ..utils import UsersContainer, DepartmentsContainer
from cromlech.browser import getSession
from dolmen.message import receive
from ul.auth import require
from uvc.design.canvas import IAboveContent
from uvc.design.canvas.menus import INavigationMenu, IPersonalMenu
from uvclight import MenuItem, menu, title
from uvclight import action, name, context, title, menuentry
from uvclight import Page, get_template, DefaultView, Fields
from zope.interface import Interface
from siguvtheme.uvclight.viewlets import BGHeader


class Departments(MenuItem):
    uvclight.name('departments')
    uvclight.title('Modulkennungen')
    uvclight.order(30)
    require('manage.departments')

    menu(INavigationMenu)
    url = action = '/departments'


class Users(MenuItem):
    uvclight.title('Benutzermanagment')
    uvclight.name('users')
    menu(INavigationMenu)
    uvclight.order(20)
    url = action = '/users'


class Admins(MenuItem):
    uvclight.title('Administratoren-Management')
    uvclight.name('admins')
    menu(INavigationMenu)
    uvclight.order(10)
    require('manage.departments')
    url = action = '/admins'


class FlashMessages(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    template = uvclight.get_template('flashmessage.cpt', __file__)
    uvclight.order(100)

    def update(self):
        messages = receive(None)
        if messages:
            self.messages = [msg for msg in messages]
        else:
            self.messages = []


@menuentry(IPersonalMenu, order=50)
class Logout(uvclight.View):
    uvclight.title('Abmelden')
    name('abmelden')
    context(Interface)
    require('zope.Public')

    def update(self):
        session = getSession()
        if session:
            if 'username' in session.keys():
                del session['username']

    def render(self):
        return self.redirect(self.application_url() + '/users')


class AppIndex(uvclight.Page):
    name('index')
    context(uvclight.IRootObject)
    require('manage.users')

    def render(self):
        return self.redirect(self.application_url() + '/users')


class BGHeader(BGHeader):
    template = get_template('bgheader.cpt', __file__)


from siguvtheme.uvclight.viewlets import DocumentActionsViewlet
from .form import ChangePWAdminBenutzer
from uvclight import view


class DocumentActionsViewlet(DocumentActionsViewlet):
    view(ChangePWAdminBenutzer)

    def render(self):
        return u""
