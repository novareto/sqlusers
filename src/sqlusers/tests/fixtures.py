# -*- coding: utf-8 -*-
# Copyright (c) 2007-2014 NovaReto GmbH
# cklinger@novareto.de

import pytest
import sql
import sql.utils

from paste.deploy import loadapp
from uvclight.tests.testing import configure


@pytest.fixture(scope="session")
def config(request):
    """loading the zca with configure.zcml of this package"""
    return configure(request, sql, 'configure.zcml')


@pytest.fixture(scope="session")
def app(request):
    """ load the paste.deploy wsgi environment from deploy.ini"""
    deploy_ini = "config=/home/novareto/slowlight/sql_project/parts/etc/deploy.ini"
    return loadapp(deploy_ini, name="main", global_conf={})


@pytest.fixture(scope="session")
def root(request):
    """ create an instance of the application"""
    return sql.utils.Root('app')

