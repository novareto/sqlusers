# -*- coding: utf-8 -*-

from ul.auth import unauthenticated_principal
from uvclight.utils import current_principal
from zope.interface import Interface
from zope.schema import TextLine, Text, Password, Int, Choice, Bool
from zope.schema.interfaces import IContextSourceBinder


class IVerifyPassword(Interface):

    verif = Password(
        title=u'Passwort wiederholen',
        required=True)


class IUser(Interface):

    login = TextLine(
        title=u"Benutzername",
        required=True)

    password = Password(
        title=u"Passwort",
        required=True)

    email = TextLine(
        title=u"E-Mail",
        required=False)


class IBenutzer(IUser):
    """
    """
    az = TextLine(
        title=u"Mitbenutzerkennung",
        defaultFactory=lambda: u'000',
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

    #nr = TextLine(
    #    title=u"Hausnummer",
    #    required=True)

    plz = TextLine(
        title=u"Postleitzahl",
        required=True)

    ort = TextLine(
        title=u"Ort",
        required=True)

    titel = TextLine(
        title=u"Titel",
        required=False)

    name = TextLine(
        title=u"Name",
        required=False)

    vorname = TextLine(
        title=u"Vorname",
        required=False)

    telefon = TextLine(
        title=u"Telefon",
        required=False)
