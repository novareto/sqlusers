# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import TextLine, Text, Password, Int


class IUser(Interface):

    login = TextLine(
        title=u"Benutzername",
        required=True)

    az = TextLine(
        title=u"Mitbenutzerkennung",
        defaultFactory=lambda: u'00',
        required=True)

    email = TextLine(
        title=u"E-Mail",
        required=False)

    name1 = TextLine(
        title=u"Firmenname",
        required=True)


class IDepartement(Interface):

    id = Int(
        title=u"Identifier",
        required=False)
    
    title = TextLine(
        title=u"Title",
        required=True)

    
class IBenutzer(IUser):
    """
    """
    password = Password(
        title=u"passwort",
        required=False)

    roles = Text(
        title=u"roles",
        required=False)

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
