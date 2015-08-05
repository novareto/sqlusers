# -*- coding: utf-8 -*-
import string
import random

from uvclight import get_template
from ..interfaces import IUser, IBenutzer, IDepartment
from ..models import Admin, Benutzer, Department
from ..utils import ADMINS, UsersContainer, AdminsContainer, DepartmentsContainer
from cromlech.sqlalchemy import get_session
from dolmen.forms.base import SuccessMarker
from dolmen.forms.crud.actions import DeleteAction, message, CancelAction
from dolmen.location import get_absolute_url
from ul.auth import require
from ul.auth import unauthenticated_principal
from uvclight.utils import current_principal
from uvc.entities.browser import IDocumentActions
from uvclight import EditForm, Form, Fields, SUCCESS, FAILURE
from dolmen.forms.crud.components import Display
from uvclight import action, name, context, title, menuentry
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import Choice
from grokcore.component import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from dolmen.forms import base
from sqlalchemy.sql.expression import func
from sqlusers import models


def genpw():
    s = "%s%s" % (string.ascii_lowercase, string.ascii_uppercase)
    d = string.digits
    return "%s%s%s%s%s%s%s%s" % (
        random.choice(s),
        random.choice(d),
        random.choice(s),
        random.choice(d),
        random.choice(s),
        random.choice(d),
        random.choice(s),
        random.choice(d),
    )


_ = MessageFactory('kuvb')


@provider(IContextSourceBinder)
def department_choice(context):
    session = get_session('sqlusers')
    user = current_principal()
    if user is not unauthenticated_principal:
        if user.id in ADMINS.keys():
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
        title=u"Modulkennung",
        source=department_choice,
        required=True)


@menuentry(IDocumentActions, order=10)
class AddAdmin(Form):
    context(AdminsContainer)
    title(u'Admin Benutzer hinzufügen')
    name('add')
    require('manage.departments')

    @property
    def fields(self):
        fields = Fields(IUser)
        principal = current_principal()
        if principal.id in ADMINS.keys():
            fields += Fields(IDepartmentChoice)
        return fields

    @property
    def action_url(self):
        return self.request.path

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
        self.flash(_(u'Die Aktion wurde erfolgreich ausgeführt.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash('Die Aktion wurde abgebrochen')
        return self.redirect(self.application_url())


@menuentry(IDocumentActions, order=10)
class EditAdminBenutzer(EditForm):
    context(IUser)
    title(u'Admin-Benutzer bearbeiten')
    name('edit')
    require('manage.users')

    @property
    def fields(self):
        fields = Fields(IUser)
        principal = current_principal()
        if principal.id in ADMINS.keys():
            fields += Fields(IDepartmentChoice)
        return fields

    @property
    def actions(self):
        actions = EditForm.actions.omit('cancel')
        return actions + MyCancelAction('Abbrechen') + DelForwardAction(title=u"Entfernen")

    @property
    def action_url(self):
        return self.request.path

@menuentry(IDocumentActions, order=20)
class DeleteAdminBenutzer(Form):
    context(IUser)
    name('delete')
    title(u'Admin-Benutzer entfernen')
    require('manage.users')
    description = title = u"Wollen Sie wirklich löschen"

    fields = Fields()

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Löschen'))
    def handle_save(self):
        session = get_session('sqlusers')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Der Benutzer wurde aus dem System gelöscht.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash('Die Aktion wurde abgebrochen')
        return self.redirect(self.application_url())


@menuentry(IDocumentActions, order=20)
class AddBenutzer(Form):
    context(UsersContainer)
    title(u'Benuzter hinzufügen')
    name('add')
    require('manage.users')
    ignoreContent = False

    @property
    def fields(self):
        fields = Fields(IBenutzer).omit('department_id')
        principal = current_principal()
        if principal.id in ADMINS.keys():
            fields += Fields(IDepartmentChoice)
        return fields

    @property
    def action_url(self):
        return self.request.path

    def update(self):
        session = get_session('sqlusers')
        principal = current_principal()
        ret = ""
        if principal.id in ADMINS.keys() or principal.department != "c":
            query = session.query(func.max(models.Benutzer.login))
            ret = 1000000
            if query.count() != 0:
                ret = int(query.one()[0]) + 1
        data = dict(
            password=genpw(),
            login=ret
        )
        self.setContentData(base.DictDataManager(data))

    def updateForm(self):
        super(AddBenutzer, self).updateForm()
        self.fieldWidgets.get('form.field.password').template = get_template('password.cpt', __file__)
        principal = current_principal()
        if principal.id in ADMINS.keys() or principal.department != "c":
            login = self.fieldWidgets.get('form.field.login')
            login._htmlAttributes['readonly'] = 'True'
        self.fieldWidgets.get('form.field.az')._htmlAttributes['maxlength'] = 3
        self.fieldWidgets.get('form.field.plz')._htmlAttributes['maxlength'] = 5

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
        az = benutzer.az
        if str(benutzer.az) != '000':
            az = ''
        lname = '%s%s%s' % (benutzer.login, benutzer.department.id, az)
        self.flash(_(u'Die Aktion wurde erfolgreich ausgeführt. Der Anmeldename des Benutzers ist %s.' % lname))
        self.redirect(self.url(self.context, self.context.key_reverse(benutzer)))
        return SUCCESS

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash('Die Aktion wurde abgebrochen')
        return self.redirect(self.application_url())


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
    title(u'Benutzer bearbeiten')
    name('edit')
    require('manage.users')

    fields = Fields(IBenutzer).omit('department_id')

    @property
    def actions(self):
        actions = EditForm.actions.omit('cancel')
        return actions + MyCancelAction('Abbrechen') + DelForwardAction(title=u"Entfernen")

    @property
    def action_url(self):
        return self.request.path

    def updateForm(self):
        super(EditBenutzer, self).updateForm()
        self.fieldWidgets.get('form.field.password').template = get_template('password_edit.cpt', __file__)
        self.fieldWidgets.get('form.field.az')._htmlAttributes['maxlength'] = 3
        self.fieldWidgets.get('form.field.plz')._htmlAttributes['maxlength'] = 5


class DisplayBenutzer(Display):
    context(IBenutzer)
    title(u'Benutzer anzeigen')
    name('index')
    require('manage.users')

    fields = Fields(IBenutzer)

    @property
    def label(self):
        return "<h2> Der Anmeldename des Benutzers ist </h2>"


@menuentry(IDocumentActions, order=20)
class DeleteBenutzer(Form):
    context(IBenutzer)
    name('delete')
    title(u'Benutzer entfernen')
    require('manage.users')
    description = title = u"Wollen Sie wirklich löschen"

    fields = Fields()

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Löschen'))
    def handle_save(self):
        session = get_session('sqlusers')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Der Benutzer wurde aus dem System gelöscht.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash('Die Aktion wurde abgebrochen')
        return self.redirect(self.application_url())


@menuentry(IDocumentActions, order=10)
class AddDepartment(Form):
    context(DepartmentsContainer)
    title(u'Modulkennung hinzufügen')
    name('add')
    require('manage.departments')

    fields = Fields(IDepartment)

    @property
    def action_url(self):
        return self.request.path

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
        self.flash(_(u'Die Aktion wurde erfolgreich ausgeführt.'))
        self.redirect(self.url(self.context))
        return SUCCESS

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash('Die Aktion wurde abgebrochen')
        return self.redirect(self.application_url())


@menuentry(IDocumentActions, order=10)
class EditDepartment(EditForm):
    context(IDepartment)
    title(u'Modulkennung bearbeiten')
    name('edit')
    require('manage.departments')

    fields = Fields(IDepartment)

    @property
    def actions(self):
        actions = EditForm.actions.omit('cancel')
        return actions + MyCancelAction('Abbrechen') + DelForwardAction(title=u"Entfernen")

    @property
    def action_url(self):
        return self.request.path


@menuentry(IDocumentActions, order=20)
class DeleteDepartment(Form):
    context(IDepartment)
    name('delete')
    title(u'Modulkennung entfernen')
    require('manage.users')
    description = title = u"Wollen Sie wirklich löschen"

    fields = Fields()

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Löschen'))
    def handle_save(self):
        session = get_session('sqlusers')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Das Objekt wurde erfolgreich gelöscht.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action('Abbrechen')
    def handle_cancel(self):
        self.flash('Die Aktion wurde abgebrochen')
        return self.redirect(self.application_url())
