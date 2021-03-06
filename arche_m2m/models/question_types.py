from __future__ import unicode_literals

from arche.api import Content
from arche.api import ContextACLMixin
from arche.api import LocalRolesMixin
from zope.interface import implementer

from arche_m2m import _
from arche_m2m.interfaces import IQuestionTypes


@implementer(IQuestionTypes)
class QuestionTypes(Content, ContextACLMixin, LocalRolesMixin):
    title = ""
    type_title = _("Question types")
    type_name = "QuestionTypes"
    add_permission = "Add %s" % type_name
    default_view = "view"
    nav_visible = True
    listing_visible = True
    search_visible = True


def includeme(config):
    config.add_content_factory(QuestionTypes)
    config.add_addable_content("QuestionTypes", ("Document", "Root"))
