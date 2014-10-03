from __future__ import unicode_literals

from arche.api import Base
from arche.api import Content
from arche.interfaces import IIndexedContent
from zope.interface import implementer
import colander
import deform

from arche_m2m import _
from arche_m2m.interfaces import IChoice
from arche_m2m.interfaces import IQuestionType
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.models.question import deferred_cluster_id
from arche_m2m.models.question import deferred_default_lang
from arche_m2m.models.question import deferred_lang_widget


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
    nav_visible = False
    listing_visible = True
    search_visible = True
    input_widget = ""

    def get_choices(self, lang):
        results = []
        for obj in self.values():
            if IChoice.providedBy(obj) and obj.language == lang:
                results.append(obj)
        return results


@implementer(IChoice, IIndexedContent)
class Choice(Base):
    type_title = _("Choice")
    type_name = "Choice"
    add_permission = "Add %s" % type_name
    title = ""
    description = ""
    cluster = ""
    language = ""


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


class EditChoiceSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Text on choice"))


class AddChoiceSchema(EditChoiceSchema):
    language = colander.SchemaNode(colander.String(),
                                   title = _("Language"),
                                   default = deferred_default_lang,
                                   widget = deferred_lang_widget)
    cluster = colander.SchemaNode(colander.String(),
                                  default = deferred_cluster_id,
                                  widget = deform.widget.HiddenWidget())


def includeme(config):
    config.add_content_factory(QuestionType)
    config.add_content_factory(Choice)
    config.add_addable_content("Choice", ("QuestionType", "Question",))
    config.add_addable_content("QuestionType", "QuestionTypes")
    config.add_content_schema('QuestionType', QuestionTypeSchema, 'edit')
    config.add_content_schema('QuestionType', QuestionTypeSchema, 'add')
    config.add_content_schema('Choice', AddChoiceSchema, 'add')
    config.add_content_schema('Choice', EditChoiceSchema, 'edit')
    config.add_content_schema('Choice', EditChoiceSchema, 'view')
