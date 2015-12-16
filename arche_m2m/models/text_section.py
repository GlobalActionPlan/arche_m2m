# -*- coding: utf-8 -*-
from arche.resources import Content
from zope.interface import implementer

from arche_m2m import _
from arche_m2m.interfaces import ITextSection
from arche_m2m.models.i18n import TranslationMixin


@implementer(ITextSection)
class TextSection(Content, TranslationMixin):
    type_title = _("Text section")
    body = ""


def includeme(config):
    config.add_content_factory(TextSection, addable_to = 'Survey')
