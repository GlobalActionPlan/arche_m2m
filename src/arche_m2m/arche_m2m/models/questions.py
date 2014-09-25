from __future__ import unicode_literals

from zope.interface import implementer
from arche.api import Content
import colander

from arche_m2m import _
from arche_m2m.interfaces import IQuestions


@implementer(IQuestions)
class Questions(Content):
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
    config.add_content_factory(Questions)
    config.add_addable_content("Questions", ("Document", "Root"))
    config.add_content_schema('Questions', QuestionsSchema, 'edit')
    config.add_content_schema('Questions', QuestionsSchema, 'add')
