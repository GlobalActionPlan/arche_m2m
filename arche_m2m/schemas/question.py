from uuid import uuid4

import colander
import deform
from arche.schemas import tagging_widget

from arche_m2m import _
from arche_m2m.interfaces import IClusterTags
from arche_m2m.schemas.i18n import deferred_default_lang, deferred_lang_widget, deferred_cluster_id


@colander.deferred
def deferred_question_type_widget(node, kw):
    view = kw['view']
    request = kw['request']
    question_type = request.GET.get('question_type', None)
    if question_type:
        return deform.widget.HiddenWidget()
    choices = []
    for obj in view.catalog_search(resolve = True, type_name = 'QuestionType'):
        title = obj.description and "%s - %s" % (obj.title, obj.description) or obj.title
        choices.append((obj.uid, title))
    return deform.widget.RadioChoiceWidget(values = choices)

@colander.deferred
def deferred_question_type_default(node, kw):
    request = kw['request']
    return request.GET.get('question_type', '')

@colander.deferred
def deferred_existing_cluster_tags(node, kw):
    """ Make sure tags don't get overwritten when forms
        are invoket on new objects that aren't attached to the
        resource tree yet.
    """
    request = kw['request']
    cluster_id = request.GET.get('cluster', '')
    view = kw['view']
    ctags = IClusterTags(view.root, {})
    return ctags.get(cluster_id, ())


class QuestionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))
    language = colander.SchemaNode(colander.String(),
                                   title = _("Language"),
                                   default = deferred_default_lang,
                                   widget = deferred_lang_widget)
    required = colander.SchemaNode(colander.Bool(),
                                   title = _("Are participants required to answer this?"),
                                   default = False,
                                   missing = False)
    question_type = colander.SchemaNode(colander.String(),
                                        title = _("Question type"),
                                        widget=deferred_question_type_widget,
                                        default = deferred_question_type_default)
    tags = colander.SchemaNode(colander.List(),
                               title = _("Tags"),
                               missing = "",
                               default = deferred_existing_cluster_tags,
                               widget = tagging_widget)
    cluster = colander.SchemaNode(colander.String(),
                                  default = deferred_cluster_id,
                                  widget = deform.widget.HiddenWidget())

def includeme(config):
    config.add_content_schema('Question', QuestionSchema, 'edit')
    config.add_content_schema('Question', QuestionSchema, 'add')
    config.add_content_schema('Question', QuestionSchema, 'view')