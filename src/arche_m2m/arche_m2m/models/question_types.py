from __future__ import unicode_literals

#from zope.interface import implementer
from arche.api import Content
#from arche.views.base import BaseView
#from arche import widgets as arche_widgets
import colander

from arche_m2m import _


#@implementer(IBase)
class QuestionTypes(Content):
    type_title = _("Question types")
    type_name = "QuestionTypes"
    add_permission = "Add %s" % type_name
    default_view = "view"
    nav_visible = True
    listing_visible = True
    search_visible = True


class QuestionTypesSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))


def includeme(config):
    config.add_content_factory(QuestionTypes)
    config.add_addable_content("QuestionTypes", ("Document", "Root"))
    config.add_content_schema('QuestionTypes', QuestionTypesSchema, 'edit')
    config.add_content_schema('QuestionTypes', QuestionTypesSchema, 'add')
