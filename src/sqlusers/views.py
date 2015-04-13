from uvclight import Page, get_template, context, name, DefaultView, Fields
from .interfaces import IBenutzer
from .utils import Container
from .models import Benutzer


class BenutzerIndex(DefaultView):
    name('index')
    context(Benutzer)

    fields = Fields(IBenutzer)
