from __future__ import unicode_literals
from unittest import TestCase

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from arche_m2m.interfaces import ITextSection


class TextSectionTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_m2m.models.text_section import TextSection
        return TextSection

    def test_verify_class(self):
        verifyClass(ITextSection, self._cut)

    def test_verify_object(self):
        verifyObject(ITextSection, self._cut())
