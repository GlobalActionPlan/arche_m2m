from __future__ import unicode_literals

from arche.api import Content
from arche.api import ContextACLMixin
from arche.api import LocalRolesMixin
from zope.interface import implementer
import colander

from arche_m2m import _
from arche_m2m.interfaces import IQuestions


@implementer(IQuestions)
class Questions(Content, ContextACLMixin, LocalRolesMixin):
    type_title = _("Questions")
    type_name = "Questions"
    add_permission = "Add %s" % type_name
#    default_view = u"view"
    nav_visible = True
    listing_visible = True
    search_visible = True


class QuestionsSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))


def includeme(config):
    config.add_content_factory(Questions, addable_to = ("Document", "Root", "Organisation"))
    config.add_content_schema('Questions', QuestionsSchema, 'edit')
    config.add_content_schema('Questions', QuestionsSchema, 'add')
