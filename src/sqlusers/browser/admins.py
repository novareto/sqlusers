# -*- coding: utf-8 -*-

import uvclight
from .form import IDepartmentChoice
from ..interfaces import IUser, IBenutzer, IDepartment
from ..models import Benutzer, Admin
from ..utils import AdminsContainer
from cromlech.browser import getSession
from dolmen.message import receive
from ul.auth import require
from uvc.design.canvas import IAboveContent
from uvc.design.canvas.menus import INavigationMenu
from uvclight import MenuItem, menu, title
from uvclight import Page, get_template, context, name, DefaultView, Fields
from zope.interface import Interface


class AdminsIndex(DefaultView):
    name('index')
    context(AdminsContainer)
    require('manage.departments')
    template = uvclight.get_template('admins.cpt', __file__)


class AdminIndex(DefaultView):
    name('index')
    context(Admin)
    require('manage.departments')

    fields = Fields(IUser) + Fields(IDepartmentChoice)

    def update(self):
        self.flash('LOS GEHTS')
        for field in self.fields:
            field.required = False
            field.readonly = False
