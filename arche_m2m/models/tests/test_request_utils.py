from __future__ import unicode_literals
from unittest import TestCase

from arche.testing import init_request_methods
from arche.testing import barebone_fixture
from pyramid import testing

from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.testing import question_fixture
from arche_m2m.interfaces import IQuestionType
from arche_m2m.interfaces import IChoice


class TestingAbstract(object):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self.config.include('arche.testing.workflow')
        self.config.include('arche_m2m')

    def tearDown(self):
        testing.tearDown()

    def fixture(self):
        root = barebone_fixture(self.config)
        question_fixture(root)
        return root


class GetQuestionWidgetTests(TestingAbstract, TestCase):

    @property
    def _fut(self):
        from arche_m2m.models.request_utils import get_question_widget as fut
        return fut

    def test_integration(self):
        request = testing.DummyRequest()
        init_request_methods(request)
        self.failUnless(hasattr(request, 'get_question_widget'))

    def test_func_from_question(self):
        root = self.fixture()
        request = testing.DummyRequest()
        init_request_methods(request)
        request.root = root
        widget = self._fut(request, root['questions']['q1'])
        self.assertTrue(IQuestionWidget.providedBy(widget))
        self.assertEqual(widget.name, 'dropdown_choice_widget')

    def test_func_from_question_type(self):
        root = self.fixture()
        request = testing.DummyRequest()
        widget = self._fut(request, root['qtypes']['qt1'])
        self.assertTrue(IQuestionWidget.providedBy(widget))
        self.assertEqual(widget.name, 'dropdown_choice_widget')


class GetQuestionTypeTests(TestingAbstract, TestCase):

    @property
    def _fut(self):
        from arche_m2m.models.request_utils import get_question_type as fut
        return fut

    def test_integration(self):
        request = testing.DummyRequest()
        init_request_methods(request)
        self.failUnless(hasattr(request, 'get_question_type'))

    def test_func(self):
        root = self.fixture()
        request = testing.DummyRequest()
        init_request_methods(request)
        request.root = root
        question_type = self._fut(request, root['questions']['q1'])
        self.assertTrue(IQuestionType.providedBy(question_type))


class GetPickedChoiceTests(TestingAbstract, TestCase):

    @property
    def _fut(self):
        from arche_m2m.models.request_utils import get_picked_choice as fut
        return fut

    def test_integration(self):
        request = testing.DummyRequest()
        init_request_methods(request)
        self.failUnless(hasattr(request, 'get_picked_choice'))

    def survey_fixture(self, root):
        from arche_m2m.models.survey import Survey
        from arche_m2m.models.survey_section import SurveySection
        root['survey'] = Survey()
        root['survey']['ss'] = ss = SurveySection()
        return ss

    def test_func(self):
        root = self.fixture()
        section = self.survey_fixture(root)
        request = testing.DummyRequest()
        request.locale_name = 'sv'
        init_request_methods(request)
        request.root = root
        q1 = root['questions']['q1']
        q2 = root['questions']['q2']
        q3 = root['questions']['q3']
        section.responses['part_uid'] = {q1.cluster: 'a', q2.cluster: 'c'}
        res1 = self._fut(request, section, q1, 'part_uid', lang = 'sv')
        self.assertEqual(res1.cluster, 'a')
        self.failUnless(IChoice.providedBy(res1))
        res2 = self._fut(request, section, q2, 'part_uid')
        self.assertEqual(res2.cluster, 'c')
        res3 = self._fut(request, section, q3, 'part_uid', lang = 'sv', default = 'fail')
        self.assertEqual(res3, 'fail')
