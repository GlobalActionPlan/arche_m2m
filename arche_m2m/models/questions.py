from __future__ import unicode_literals

from arche.api import Content
from arche.api import ContextACLMixin
from arche.api import LocalRolesMixin
from zope.interface import implementer

from arche_m2m import _
from arche_m2m.interfaces import IQuestions


@implementer(IQuestions)
class Questions(Content, ContextACLMixin, LocalRolesMixin):
    type_title = _("Questions")
    type_name = "Questions"
    add_permission = "Add %s" % type_name
    nav_visible = True
    listing_visible = True
    search_visible = True


def includeme(config):
    config.add_content_factory(Questions, addable_to = ("Document", "Root", "Organisation"))
