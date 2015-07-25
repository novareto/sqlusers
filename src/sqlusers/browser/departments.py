# -*- coding: utf-8 -*-

import uvclight
from ..interfaces import IBenutzer, IDepartment
from ..models import Benutzer
from ..utils import UsersContainer, DepartmentsContainer
from cromlech.browser import getSession
from dolmen.message import receive
from ul.auth import require
from uvc.design.canvas import IAboveContent
from uvc.design.canvas.menus import INavigationMenu
from uvclight import MenuItem, menu, title
from uvclight import Page, get_template, context, name, DefaultView, Fields
from zope.interface import Interface


class DepartmentIndex(DefaultView):
    name('index')
    context(IDepartment)
    require('manage.departments')

    fields = Fields(IDepartment)

    def update(self):
        for field in self.fields:
            field.required = False
            field.readonly = False
