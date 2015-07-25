# -*- coding: utf-8 -*-

from ul.auth import unauthenticated_principal
from uvclight.utils import current_principal
from zope.interface import Interface
from zope.schema import TextLine, Text, Password, Int, Choice, Bool
from zope.schema.interfaces import IContextSourceBinder


class IUser(Interface):

    login = TextLine(
        title=u"Benutzername",
        required=True)

    password = Password(
        title=u"passwort",
        required=False)

    email = TextLine(
        title=u"E-Mail",
        required=False)


class IDepartment(Interface):
    """
    """
    id = TextLine(
        title=u"Identifier",
        required=True)

    title = TextLine(
        title=u"Title",
        required=True)


class IBenutzer(IUser):
    """
    """
    az = TextLine(
        title=u"Mitbenutzerkennung",
        defaultFactory=lambda: u'00',
        required=True)

    name1 = TextLine(
        title=u"Firmenname",
        required=True)
    
    name2 = TextLine(
        title=u"Name2",
        required=False)

    name3 = TextLine(
        title=u"Name3",
        required=False)

    strasse = TextLine(
        title=u"Strasse",
        required=True)

    nr = TextLine(
        title=u"Hausnummer",
        required=True)

    plz = TextLine(
        title=u"Postleitzahl",
        required=True)

    ort = TextLine(
        title=u"Ort",
        required=True)
