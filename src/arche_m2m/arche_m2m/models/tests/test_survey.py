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
        from arche_m2m.models.survey import Survey
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

    def test_get_participants_data(self):
        obj = self._cut()
        obj.create_token("testing@example.com")
        from arche_m2m.models.survey_section import SurveySection
        obj['ss'] = ss = SurveySection()
        ss.responses["testing@example.com"] = {'one': 1, 'two': "tvaa"}
        self.assertEqual(len(obj.get_participants_data()), 1)
