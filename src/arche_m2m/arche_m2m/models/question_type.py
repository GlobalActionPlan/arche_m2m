from __future__ import unicode_literals

from zope.interface import implementer
from arche.api import Base
from arche.api import Content
import colander
import deform

from arche_m2m.interfaces import IChoice
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import IQuestionType
from arche_m2m import _


@implementer(IQuestionType)
class QuestionType(Content):
    """ This is the persistent information about a question type.
        It's the same for all kind of types - it simply stores information
        on what adapters to use.
    """
    type_title = _("Question type")
    type_name = "QuestionType"
    add_permission = "Add %s" % type_name
    #default_view = "view"
    nav_visible = True
    listing_visible = True
    search_visible = True
    input_widget = ""
    #Have settings or similar stored here? Probably


@implementer(IChoice)
class Choice(Base):
    type_title = _("Choice")
    type_name = "Choice"
    add_permission = "Add %s" % type_name
    title = ""


@colander.deferred
def deferred_input_widget(node, kw):
    values = []
    request = kw['request']
    context = kw['context']
    for (name, widget) in request.registry.getAdapters([context], IQuestionWidget):
        values.append((name, widget.title))
    return deform.widget.RadioChoiceWidget(values=values)


class QuestionTypeSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title=_("Title"))
    input_widget = colander.SchemaNode(colander.String(),
                                       title=_("Input widget"),
                                       missing="",
                                       widget=deferred_input_widget, )


class ChoiceSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Text on choice"))





def includeme(config):
    config.add_content_factory(QuestionType)
    config.add_content_factory(Choice)
    config.add_addable_content("Choice", "QuestionType")
    config.add_addable_content("QuestionType", "QuestionTypes")
    #config.add_content_schema('QuestionType', QuestionTypeSchema, 'view')
    config.add_content_schema('QuestionType', QuestionTypeSchema, 'edit')
    config.add_content_schema('QuestionType', QuestionTypeSchema, 'add')
    config.add_content_schema('Choice', ChoiceSchema, 'add')
    config.add_content_schema('Choice', ChoiceSchema, 'edit')
    config.add_content_schema('Choice', ChoiceSchema, 'view')
