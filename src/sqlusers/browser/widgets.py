import uvclight

import grokcore.component as grok
from dolmen.forms.base.widgets import DisplayFieldWidget
from dolmen.forms.ztk.widgets.password import PasswordField


class PasswordDisplayWidget(DisplayFieldWidget):
    grok.adapts(PasswordField, None, None)

    template = uvclight.get_template('password_input.cpt', __file__)
