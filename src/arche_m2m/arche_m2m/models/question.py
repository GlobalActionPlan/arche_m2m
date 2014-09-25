from __future__ import unicode_literals
from uuid import uuid4

from arche import security
from arche.api import Content
from arche.views.base import BaseForm
from zope.interface import implementer
import colander
import deform

from arche_m2m.interfaces import IQuestion
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m import _


@implementer(IQuestion)
class Question(Content):
    type_title = _("Question")
    type_name = "Question"
    add_permission = "Add %s" % type_name
#    default_view = u"view"
    nav_visible = True
    listing_visible = True
    search_visible = True
    question_type = None
    language = ''
    cluster = ''


@colander.deferred
def deferred_question_type_widget(node, kw):
    view = kw['view']
    choices = []
    for obj in view.catalog_search(resolve = True, type_name = 'QuestionType'):
        title = obj.description and "%s - %s" % (obj.title, obj.description) or obj.title
        choices.append((obj.uid, title))
    return deform.widget.RadioChoiceWidget(values = choices)

@colander.deferred
def deferred_lang_widget(node, kw):
    request = kw['request']
    choices = []
    languages = request.registry.settings.get('m2m.languages', 'en').split()
    for lang in languages:
        choices.append((lang, lang))
    return deform.widget.SelectWidget(values = choices)

@colander.deferred
def deferred_default_lang(node, kw):
    request = kw['request']
    return request.GET.get('language', request.locale_name)

@colander.deferred
def deferred_cluster_id(node, kw):
    request = kw['request']
    return request.GET.get('cluster', str(uuid4()))


class QuestionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))
    language = colander.SchemaNode(colander.String(),
                                   title = _("Language"),
                                   default = deferred_default_lang,
                                   widget = deferred_lang_widget)
    question_type = colander.SchemaNode(colander.String(),
                                        title = _("Question type"),
                                        widget=deferred_question_type_widget,)
    cluster = colander.SchemaNode(colander.String(),
                                  missing = "",
                                  default = deferred_cluster_id,
                                  widget = deform.widget.HiddenWidget())


def includeme(config):
    config.add_content_factory(Question)
    config.add_addable_content("Question", "Questions")
    config.add_content_schema('Question', QuestionSchema, 'edit')
    config.add_content_schema('Question', QuestionSchema, 'add')
    config.add_content_schema('Question', QuestionSchema, 'view')

