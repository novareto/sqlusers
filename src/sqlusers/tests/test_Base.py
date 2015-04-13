from cromlech.browser.testing import TestRequest
from grokcore.component import Context
from zope.component import getMultiAdapter


class TestClass:
    request = TestRequest()
    context = Context()

    def test_example(self):
        assert 1==1

#    def test_view(self, config, root):
#        view = getMultiAdapter((root, self.request), name='index')
#        view.update()
#        assert "HALLO WELT" == view.render()

