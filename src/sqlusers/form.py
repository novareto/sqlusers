from uvclight import EditForm, Form, Fields, SUCCESS, FAILURE
from uvclight import action, name, context, title, menuentry
from cromlech.sqlalchemy import get_session
from uvc.design.canvas import IContextualActionsMenu
from zope.interface import Interface
from .interfaces import IBenutzer
from .models import Benutzer
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('kuvb')


@menuentry(IContextualActionsMenu, order=10)
class AddBenutzer(Form):
    context(Interface)
    name('add.user')

    fields = Fields(IBenutzer)

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('sqlusers')
        benutzer = Benutzer(**data)
        session.add(benutzer)
        session.flush()
        session.refresh(benutzer)
        self.flash(_(u'Added with success.'))
        self.redirect(self.application_url())
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class EditBenutzer(EditForm):
    context(IBenutzer)
    name('edit')

    fields = Fields(IBenutzer)

    @property
    def action_url(self):
        return self.request.path


@menuentry(IContextualActionsMenu, order=20)
class DeleteBenutzer(Form):
    context(IBenutzer)
    name('delete')

    fields = Fields()

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('sqlusers')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS
