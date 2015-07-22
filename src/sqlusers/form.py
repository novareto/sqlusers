# -*- coding: utf-8 -*-

from uvclight import EditForm, Form, Fields, SUCCESS, FAILURE
from uvclight import action, name, context, menuentry
from ul.auth import require
from cromlech.sqlalchemy import get_session
from uvc.design.canvas import IContextualActionsMenu
from zope.interface import Interface
from .interfaces import IBenutzer
from .models import Benutzer
from zope.i18nmessageid import MessageFactory
from dolmen.forms.crud.actions import DeleteAction, message, CancelAction
from dolmen.location import get_absolute_url
from dolmen.forms.base import SuccessMarker


_ = MessageFactory('kuvb')


@menuentry(IContextualActionsMenu, order=10)
class AddBenutzer(Form):
    context(Interface)
    name('add.user')
    require('manage.users')

    fields = Fields(IBenutzer)

    @property
    def action_url(self):
        return self.request.path

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash('Die Aktion wurde abgebrochen')
        return self.redirect(self.application_url())

    @action(_(u'Anlegen'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('sqlusers')
        if session.query(Benutzer).filter(Benutzer.login == data['login'], Benutzer.az == data['az']).count():
            self.flash(u'Es gibt bereits einen Benutzer mit diesen Kriterien')
            return
        benutzer = Benutzer(**data)
        session.add(benutzer)
        session.flush()
        session.refresh(benutzer)
        self.flash(_(u'Added with success.'))
        self.redirect(self.application_url())
        return SUCCESS


class MyDeleteAction(DeleteAction):

    def available(self, form):
        return True

    def __call__(self, form):
        content = form.getContentData().getContent()
        container = content.__parent__
        session = get_session('sqlusers')
        session.delete(content)
        form.status = self.successMessage
        message(form.status)
        url = get_absolute_url(container, form.request)
        return SuccessMarker('Deleted', True, url=url)


class MyCancelAction(CancelAction):

    def __call__(self, form):
        form.flash(u'Die Aktion wurde abgebrochen')
        url = form.application_url()
        return SuccessMarker('Canceled', True, url=url)


class DelForwardAction(CancelAction):

    def __call__(self, form):
        form.flash(u'Bitte bestätigen Sie die Löschung')
        url = form.url(form.getContent(), 'delete')
        return SuccessMarker('Canceled', True, url=url)


@menuentry(IContextualActionsMenu, order=10)
class EditBenutzer(EditForm):
    context(IBenutzer)
    name('edit')
    require('manage.users')

    fields = Fields(IBenutzer)

    @property
    def actions(self):
        actions = EditForm.actions.omit('cancel')
        return actions + MyCancelAction('Abbrechen') + DelForwardAction(title=u"Entfernen")

    @property
    def action_url(self):
        return self.request.path


@menuentry(IContextualActionsMenu, order=20)
class DeleteBenutzer(Form):
    context(IBenutzer)
    name('delete')
    require('manage.users')
    description = title = u"Wollen Sie wirklich löschen"

    fields = Fields()

    @property
    def action_url(self):
        return self.request.path

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash('Die Aktion wurde abgebrochen')
        return self.redirect(self.application_url())

    @action(_(u'Löschen'))
    def handle_save(self):
        session = get_session('sqlusers')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS
