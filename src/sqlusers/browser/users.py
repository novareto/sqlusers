# -*- coding: utf-8 -*-

import uvclight
from ..interfaces import IBenutzer
from ..models import Benutzer
from ..utils import UsersContainer
from cromlech.browser import getSession
from dolmen.message import receive
from ul.auth import require
from uvc.design.canvas import IAboveContent
from uvc.design.canvas.menus import INavigationMenu
from uvclight import MenuItem, menu, title
from uvclight import Page, get_template, context, name, DefaultView, Fields
from zope.interface import Interface


class BenutzerIndex(DefaultView):
    name('index')
    context(Benutzer)
    require('manage.users')

    fields = Fields(IBenutzer)

    @property
    def label(self):
        az = self.context.az
        if str(az) == '000':
            az = ""
        return u"Anmeldename: %s%s" % (self.context.login, az)

    def update(self):
        for field in self.fields:
            field.required = False
            field.readonly = False

    @uvclight.action(u'zur Startseite')
    def handle_back(self):
        self.redirect(self.application_url())
