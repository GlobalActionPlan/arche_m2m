from unittest import TestCase

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from arche_m2m.interfaces import ISurveySection


class SurveySectionTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_m2m.models.survey_section import SurveySection
        return SurveySection

    def test_verify_class(self):
        verifyClass(ISurveySection, self._cut)

    def test_verify_object(self):
        verifyObject(ISurveySection, self._cut())

    def test_question_ids_unique(self):
        obj = self._cut()
        obj.question_ids = ['1', '2']
        self.assertEqual(obj.question_ids, ('1', '2'))
        try:
            obj.question_ids = ['1', '1', '2']
            self.fail("ValueError not raised with non-unique values")
        except ValueError:
            pass
