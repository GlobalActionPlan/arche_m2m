from __future__ import unicode_literals
from unittest import TestCase

from arche.interfaces import IPopulator
from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from arche_m2m.interfaces import IQuestion
from arche_m2m.interfaces import IClusterTags


class QuestionTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_m2m.models.question import Question
        return Question

    def _fixture(self):
        from arche.api import Root
        root = Root()
        request = testing.DummyRequest(context = root)
        self.config = testing.setUp(request = request, registry = self.config.registry)
        return root

    def test_verify_class(self):
        verifyClass(IQuestion, self._cut)

    def test_verify_object(self):
        verifyObject(IQuestion, self._cut())

    def test_tags_set_single(self):
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self._fixture()
        self.config.include('arche_m2m.models.cluster_tags')
        question = self._cut(tags = ('Hello',), cluster = '1')
        self.assertEqual(question.tags, ('Hello',))

    def test_tags_set_multiple(self):
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        root = self._fixture()
        self.config.include('arche_m2m.models.cluster_tags')
        root['q1'] = self._cut(tags = ['one', 'two'], cluster = '1')
        second = self._cut(tags = ['one', 'two', 'three'], cluster = '1')
        self.assertEqual(root['q1'].tags, second.tags)

    def test_tags_set_updates_catalog(self):
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self.config.include('arche.models.workflow')
        self.config.include('arche_m2m')
        root = self._fixture()
        root['q1'] = self._cut(tags = ['one', 'two'], cluster = '1')
        second = self._cut(tags = ['one', 'two', 'three'], cluster = '1')
        root['q2'] = second
        self.assertEqual(root.catalog.search(tags = 'three')[0].total, 2) 

    def test_deleting_last_question_clears_global_tags(self):
        self.config.include('arche.testing')
        self.config.include('arche.testing.catalog')
        self.config.include('arche.models.workflow')
        self.config.include('arche_m2m')
        root = self._fixture()
        root['q1'] = self._cut(tags = ['one', 'two'], cluster = '1')
        root['q2'] = self._cut(tags = ['one', 'two', 'three'], cluster = '1')
        ctags = IClusterTags(root)
        self.assertIn('1', ctags)
        del root['q1']
        self.assertIn('1', ctags)
        del root['q2']
        self.assertNotIn('1', ctags)
