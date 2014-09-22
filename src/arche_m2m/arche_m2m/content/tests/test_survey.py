from unittest import TestCase

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


from arche_m2m.interfaces import ISurvey

class SurveyTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_m2m.content.survey import Survey
        return Survey

    def test_verify_class(self):
        verifyClass(ISurvey, self._cut)

    def test_verify_object(self):
        verifyObject(ISurvey, self._cut())

    def test_create_token(self):
        email = "dummy@example.com"
        obj = self._cut()
        token = obj.create_token(email)
        self.assertTrue(token.valid)
        self.assertEqual(len(obj.tokens), 1)
