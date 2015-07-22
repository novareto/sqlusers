# -*- coding: utf-8 -*-

import uvclight

from ul.auth import require
from .models import Benutzer
from .interfaces import IBenutzer
from dolmen.message import receive
from uvc.design.canvas import IAboveContent
from uvc.design.canvas.menus import INavigationMenu
from uvclight import context, name, DefaultView, Fields
from uvclight import MenuItem, menu, title
from zope.interface import Interface
from cromlech.browser import getSession


class BenutzerIndex(DefaultView):
    name('index')
    context(Benutzer)
    require('manage.users')

    fields = Fields(IBenutzer)

    def update(self):
        self.flash('LOS GEHTS')
        for field in self.fields:
            field.required = False
            field.readonly = False


class CreateUserEntry(uvclight.MenuItem):
    uvclight.title(u'Benuzter anlegen')
    uvclight.auth.require('manage.users')
    uvclight.menu(INavigationMenu)

    @property
    def action(self):
        return self.view.url(self.context, 'add.user')


class FlashMessages1(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    template = uvclight.get_template('flashmessage.cpt', __file__)
    uvclight.order(100)

    def update(self):
        messages = receive(None)
        if messages:
            self.messages = [msg for msg in messages]
        else:
            self.messages = []


class LogoutMenu(MenuItem):
    context(Interface)
    menu(INavigationMenu)
    title(u'Logout')

    @property
    def action(self):
        return self.view.application_url() + '/abmelden'


class Logout(uvclight.View):
    name('abmelden')
    context(uvclight.IRootObject)
    require('zope.Public')

    def update(self):
        session = getSession()
        if session:
            del session['username']

    def render(self):
        return self.redirect(self.application_url())
