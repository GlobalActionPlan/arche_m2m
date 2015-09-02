# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from arche_m2m.interfaces import ILangCodes


class LangCodesTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_m2m.models.i18n import LangCodes
        return LangCodes

    def test_verify_class(self):
        verifyClass(ILangCodes, self._cut)

    def test_verify_object(self):
        verifyObject(ILangCodes, self._cut(self.config.registry))

    def test_init(self):
        self.config.registry.settings['m2m.languages'] = 'en sv fr'
        util = self._cut(self.config.registry)
        self.failUnless(set(util), set(['en', 'sv', 'fr']))
        self.assertEqual(util['fr'], "fran\xe7ais (French)")
