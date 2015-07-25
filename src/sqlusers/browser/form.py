# -*- coding: utf-8 -*-

from ..interfaces import IUser, IBenutzer, IDepartment
from ..models import Admin, Benutzer, Department
from ..utils import UsersContainer, AdminsContainer, DepartmentsContainer
from cromlech.sqlalchemy import get_session
from dolmen.forms.base import SuccessMarker
from dolmen.forms.crud.actions import DeleteAction, message, CancelAction
from dolmen.location import get_absolute_url
from ul.auth import require
from ul.auth import unauthenticated_principal
from uvclight.utils import current_principal
from uvc.entities.browser import IDocumentActions
from uvc.design.canvas.menus import INavigationMenu
from uvclight import EditForm, Form, Fields, SUCCESS, FAILURE
from uvclight import action, name, context, title, menuentry
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import Choice
from grokcore.component import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


_ = MessageFactory('kuvb')


@provider(IContextSourceBinder)
def department_choice(context):
    session = get_session('sqlusers')
    user = current_principal()
    if user is not unauthenticated_principal:
        if user.id == 'admin':
            departments = session.query(Department).all()
        else:
            departments = [session.query(Department).get(user.department)]
    else:
        departments = []

    return SimpleVocabulary([
        SimpleTerm(value=dep.id, token=dep.id, title='%s' % dep.title)
        for dep in departments])


class IDepartmentChoice(Interface):
    """
    """
    department_id = Choice(
        title=u"Department",
        source=department_choice,
        required=True)


@menuentry(IDocumentActions, order=10)
class AddAdmin(Form):
    context(AdminsContainer)
    name('add')
    require('manage.departments')

    @property
    def fields(self):
        fields = Fields(IUser)
        principal = current_principal()
        if principal.id == 'admin':
            fields += Fields(IDepartmentChoice)
        return fields
            
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
        if session.query(Admin).get(data['login']) is not None:
            self.flash(u'Es gibt bereits einen Benutzer mit diesen Kriterien')
            return

        if 'department_id' not in data:
            principal = current_principal()
            data['department_id'] = principal.department

        admin = Admin(**data)
        session.add(admin)
        session.flush()
        session.refresh(admin)
        self.flash(_(u'Added with success.'))
        self.redirect(self.application_url())
        return SUCCESS
    

@menuentry(IDocumentActions, order=20)
class AddBenutzer(Form):
    context(UsersContainer)
    name('add')
    require('manage.users')

    @property
    def fields(self):
        fields = Fields(IBenutzer)
        principal = current_principal()
        if principal.id == 'admin':
            fields += Fields(IDepartmentChoice)
        return fields
            
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
        if session.query(Benutzer).filter(
                Benutzer.login == data['login'], Benutzer.az == data['az']).count():
            self.flash(u'Es gibt bereits einen Benutzer mit diesen Kriterien')
            return

        if 'department_id' not in data:
            principal = current_principal()
            data['department_id'] = principal.department

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


@menuentry(IDocumentActions, order=10)
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


@menuentry(IDocumentActions, order=20)
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


@menuentry(IDocumentActions, order=10)
class AddDepartment(Form):
    context(DepartmentsContainer)
    name('add')
    require('manage.departments')

    fields = Fields(IDepartment)

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

        department = Department(**data)
        session = get_session('sqlusers')
        session.add(department)
        session.flush()
        session.refresh(department)
        self.flash(_(u'Added with success.'))
        self.redirect(self.url(self.context))
        return SUCCESS