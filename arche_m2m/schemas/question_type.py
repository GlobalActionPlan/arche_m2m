from __future__ import unicode_literals

import colander
import deform

from arche_m2m import _
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.schemas.i18n import deferred_default_lang
from arche_m2m.schemas.i18n import deferred_lang_widget
from arche_m2m.schemas.i18n import deferred_cluster_id


@colander.deferred
def deferred_input_widget(node, kw):
    request = kw['request']
    values = []
    values.extend([(x.name, x.factory) for x in request.registry.registeredAdapters() if x.provided == IQuestionWidget])
    return deform.widget.RadioChoiceWidget(values = values,
                                           template = "object_radio_choice",
                                           readonly_template = "readonly/object_radio_choice")



class QuestionTypeSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title=_("Title"))


class EditQuestionTypeSchema(QuestionTypeSchema):
    pass


class AddQuestionTypeSchema(QuestionTypeSchema):
    input_widget = colander.SchemaNode(colander.String(),
                                       title=_("Input widget"),
                                       missing="",
                                       widget=deferred_input_widget,)


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
    config.add_content_schema('QuestionType', AddQuestionTypeSchema, 'add')
    config.add_content_schema('QuestionType', EditQuestionTypeSchema, 'edit')
    config.add_content_schema('Choice', AddChoiceSchema, 'add')
    config.add_content_schema('Choice', EditChoiceSchema, ('edit', 'view'))
