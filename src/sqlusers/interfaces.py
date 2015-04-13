from zope.schema import TextLine, Text, Password
from zope.interface import Interface



class IUser(Interface):

    login = TextLine(
        title=u"login",
        required=False)

    az = TextLine(
        title=u"az",
        required=False)

    email = TextLine(
        title=u"email",
        required=False)

    name1 = TextLine(
        title=u"name1",
        required=False)


class IBenutzer(IUser):
    """
    """

    password = Password(
        title=u"password",
        required=False)

    roles = Text(
        title=u"roles",
        required=False,
        )

    name2 = TextLine(
        title=u"name2",
        required=False)

    name3 = TextLine(
        title=u"name3",
        required=False)

    strasse = TextLine(
        title=u"strasse",
        required=True)

    nr = TextLine(
        title=u"nr",
        required=True)

    plz = TextLine(
        title=u"plz",
        required=False)

    ort = TextLine(
        title=u"ort",
        required=False)

    oid = TextLine(
        title=u"oid",
        required=False)

    merkmal = TextLine(
        title=u"merkmal",
        required=False)

