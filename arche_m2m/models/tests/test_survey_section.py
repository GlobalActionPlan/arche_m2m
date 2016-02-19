from unittest import TestCase

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from arche.testing import barebone_fixture
from arche_m2m.interfaces import ISurveySection
from arche_m2m.testing import question_fixture


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

    def test_get_questions(self):
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self.config.include('arche.testing.workflow')
        self.config.include('betahaus.viewcomponent')
        self.config.include('arche_m2m')
        root = barebone_fixture(self.config)
        question_fixture(root)
        root['survey_section'] = obj = self._cut()
        obj.question_ids = ['q_cluster', 'q_cluster2', 'q_cluster3']
        self.assertEqual(len(obj.get_questions(None)), 4) #All
        self.assertEqual(len(obj.get_questions('en')), 1)
        self.assertEqual(len(obj.get_questions('sv')), 3)
