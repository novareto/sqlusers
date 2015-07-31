# -*- coding: utf-8 -*-

from math import log

from uvclight import Form, Fields, Action, Actions
from uvclight import get_template, context, name, title
from ul.auth import require

from dolmen.batch import Batcher
from dolmen.forms.base.errors import Error
from dolmen.forms.base.markers import SUCCESS, FAILURE, NO_VALUE
from dolmen.forms.ztk import InvariantsValidation

from ..utils import UsersContainer
from ..interfaces import IUser
from .resources import css
from ..models import Benutzer


def get_dichotomy_batches(batches, N, n):
    """
    A dummy batch object::
    """
    # normalize
    n = max(1, min(n, N))
    if not n:
        n = 1
    # number of iteration to find n doing a dichotomic search in 1..N
    log_position = int(log(max(N/n, 1), 2))

    markers = set([1, max(1, n-1), n, min(n+1, N), N])
    # always middle
    markers.add(int(N/2))
    # previous numbers in a dichotomich search
    for i in range(log_position)[-2:]:
        markers.add(int(N / 2**i))
    # next numbers  in a dichotomich search
    i = int(N / 2**(log_position+1))
    markers.add(i)
    markers.add(min(n + i, N))

    for i in range(log_position, ):
        markers.add(int(N / 2**i))

    # if we have less than 8 buttons, add some around current
    maxlen = min(8, N)  # maybe N < 8 !
    i = 2
    while len(markers) < maxlen:
        markers.add(min(n+i, N))
        markers.add(max(n-i, 1))
        i += 1
    markers = list(markers)
    markers.sort()

    last = 0
    for b in markers:
        if b and b > last:

            batch = batches[b - 1]

            if last and b > last + 1:
                yield 'ellipsis', '...'

            if b == n:
                yield 'current', batch
            elif b > n:
                yield 'next', batch
            else:
                yield 'previous', batch

            last = b


def iter_batches(batches, N, n):
    for b in batches:
        if b.number == n:
            yield 'current', b
        elif b.number > n:
            yield 'next', b
        else:
            yield 'previous', b


class SearchBatcher(Batcher):

    template = get_template('batch.pt', __file__)

    num_items = None
    """set num_items on batch instance
    if you want to display total number of items"""

    def get_batches(self):
        N = self.batch.batches.total
        n = self.batch.number
        if N <= 8:
            return iter_batches(self.batch.batches, N, n)
        return get_dichotomy_batches(self.batch.batches, N, n)


class SearchAction(Action):

    def search(self, form, data):
        session = form.context.session
        query = session.query(form.context.model)

        for field, value in data.items():
            if value:
                if value is not NO_VALUE:
                    prop = getattr(Benutzer, field)
                    if '*' in value:
                        like = value.replace('*', '%')
                        query = query.filter(prop.like(like))
                    else:
                        query = query.filter(prop == value)

            sorting = form.sorter
            if sorting[0] == '-':
                sorter = getattr(Benutzer, form.sorter[1:])
                query = query.order_by(sorter.desc())
            else:
                sorter = getattr(Benutzer, form.sorter)
                query = query.order_by(sorter)

        total = query.count()
        query = query.limit(form.batch_size)
        query = query.offset(form.batch_start)
        return total, query.all()

    def __call__(self, form):
        data, errors = form.extractData()
        form.extracted = data

        #if errors:
        #    return FAILURE

        if not data:
            form.errors.add(Error('form', 'You need at least one value'))
            return FAILURE

        form.search_len, form.search_results = self.search(form, data)
        return SUCCESS


class SearchPage(Form):
    name('index')
    context(UsersContainer)
    require('manage.users')

    template = get_template('search.pt', __file__)

    fields = Fields(IUser)
    sorter = 'login'
    sorter_values = {
        field.identifier: u'▲ ' + field.title for field in fields
    }
    sorter_values.update({
        u'-' + field.identifier: u'▼ ' + field.title for field in fields
    })

    search_results = tuple()
    dataValidators = [InvariantsValidation]
    postOnly = False
    formMethod = 'GET'
    enctype = 'application/x-www-form-urlencoded'

    batch_size = 25

    actions = Actions(SearchAction(u'Suchen'))

    def update(self):
        for field in self.fields:
            field.required = False
            field.readonly = False

    @property
    def title(self):
        return '%s (%s)' % (
            title.bind(default='Suche').get(self),
            getattr(self.context, 'title', self.context.__name__))

    @property
    def results(self):
        for result in self.search_results:
            yield {
                'url': self.base + '/' + self.context.key_reverse(result),
                'title': '%s%s%s (%s)' % (
                    result.login, result.department.id, result.az, result.email),
                'obj': result,
            }

    def updateActions(self):
        css.need()
        self.base = self.url(self.context)
        self.search_len = 0
        self.sorter = self.request.form.get('sorter', self.sorter)
        self.extracted = {}
        self.batcher = SearchBatcher(
            self, self.request, size=self.batch_size)
        self.batch_start, self.batch_size = self.batcher.batch_info()

        action, marker = self.actions.process(self, self.request)
        if self.search_len:
            self.batcher.update(range(0, self.search_len))

        return action, marker
