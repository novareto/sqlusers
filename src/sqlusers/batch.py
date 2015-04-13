# -*- coding: utf-8 -*-

import copy
import csv
import datetime
import dolmen.menu
import types

from math import log

from uvclight import Form, Page, View, Fields, Action, Actions
from uvclight import get_template, context, name, title

from cStringIO import StringIO
from cromlech.browser import ITraverser, IRequest
from cromlech.browser.exceptions import HTTPFound
from cromlech.browser.utils import redirect_exception_response
from cromlech.webob.response import Response
from dolmen.batch import Batcher
from dolmen.forms.base.errors import Error
from dolmen.forms.base.markers import SUCCESS, FAILURE, NOTHING_DONE, NO_VALUE
from dolmen.forms.ztk import InvariantsValidation
from dolmen.view import make_layout_response
from z3c.batching.batch import Batch
from zope.cachedescriptors.method import cachedIn
from zope.cachedescriptors.property import Lazy
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.security import checkPermission

from .models import Benutzer
from .utils import Container
from .interfaces import IUser
from .resources import css


def get_dichotomy_batches(batches, N, n):
    """
    A dummy batch object::

      >>> batch = range(1, 101)  # have enough numbers

    Help user make a dichotomic search::

      >>> list(get_dichotomy_batches(batch, 100,50))
      [('previous', 1), ('ellipsis', '...'), ('previous', 25), ('ellipsis', '...'), ('previous', 48), ('previous', 49), ('current', 50), ('next', 51), ('next
', 52), ('ellipsis', '...'), ('next', 75), ('ellipsis', '...'), ('next', 100)]
      >>> list(get_dichotomy_batches(batch, 100,25))
      [('previous', 1), ('ellipsis', '...'), ('previous', 12), ('ellipsis', '...'), ('previous', 24), ('current', 25), ('next', 26), ('ellipsis', '...'), ('n
ext', 37), ('ellipsis', '...'), ('next', 50), ('ellipsis', '...'), ('next', 100)]

    limit cases::

      >>> list(get_dichotomy_batches(batch, 1,1))
      [('current', 1)]
      >>> list(get_dichotomy_batches(batch, 100,1))
      [('current', 1), ('next', 2), ('next', 3), ('ellipsis', '...'), ('next', 6), ('ellipsis', '...'), ('next', 12), ('ellipsis', '...'), ('next', 25), ('el
lipsis', '...'), ('next', 50), ('ellipsis', '...'), ('next', 100)]
      >>> list(get_dichotomy_batches(batch, 100,1))
      [('current', 1), ('next', 2), ('next', 3), ('ellipsis', '...'), ('next', 6), ('ellipsis', '...'), ('next', 12), ('ellipsis', '...'), ('next', 25), ('el
lipsis', '...'), ('next', 50), ('ellipsis', '...'), ('next', 100)]

    Buggy cases do not break::
    >>> list(get_dichotomy_batches(batch, 100,150)) == (
    ...     list(get_dichotomy_batches(batch, 100,100)))
    True
    >>> list(get_dichotomy_batches(batch, 100,-20)) == (
    ...     list(get_dichotomy_batches(batch, 100,1)))
    True

    
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
        query = session.query(Benutzer)
        total = query.count()

        for field, value in data.items():
            if value:
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

        query = query.limit(form.batch_size)
        query = query.offset(form.batch_start)

        return total, query.all()

    def __call__(self, form):
        data, errors = form.extractData()
        form.extracted = data

        if errors:
            return FAILURE

        if not data:
            form.errors.add(Error('form', 'You need at least one value'))
            return FAILURE

        form.search_len, form.search_results = self.search(form, data)
        return SUCCESS


class SearchPage(Form):
    name('index')
    context(Container)
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

    actions = Actions(SearchAction(u'Search'))

    @property
    def title(self):
        return title.bind(default='Search').get(self)

    @property
    def results(self):
        for result in self.search_results:
            yield {
                'url': self.base + '/' + self.context.key_reverse(result),
                'title': '%s %s (%s)' % (result.login, result.az, result.email),
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
