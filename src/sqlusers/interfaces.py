from zope.schema import TextLine, Password
from zope.interface import Interface


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


class IBenutzer(IUser):
    """
    """

    password = Password(
        title=u"Passwort",
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
