from __future__ import unicode_literals
from uuid import uuid4

from arche.api import Content
from arche.interfaces import ICataloger
from arche.interfaces import IObjectAddedEvent
from arche.interfaces import IObjectUpdatedEvent
from arche.interfaces import IObjectWillBeRemovedEvent
from arche.schemas import tagging_widget
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from zope.interface import implementer
import colander
import deform

from arche_m2m import _
from arche_m2m.interfaces import IChoice
from arche_m2m.interfaces import IClusterTags
from arche_m2m.interfaces import IQuestion


@implementer(IQuestion)
class Question(Content):
    type_title = _("Question")
    type_name = "Question"
    add_permission = "Add %s" % type_name
#    default_view = u"view"
    nav_visible = True
    listing_visible = True
    search_visible = True
    question_type = ''
    language = ''
    cluster = ''
    required = False

    def __init__(self, **kw):
        #Make sure cluster is set before anytjing else!
        self.cluster = kw.pop('cluster', '')
        super(Question, self).__init__(**kw)

    def get_choices(self, lang):
        results = []
        for obj in self.values():
            if IChoice.providedBy(obj) and obj.language == lang:
                results.append(obj)
        return results

    @property
    def tags(self):
        request = get_current_request()
        root = find_root(request.context)
        ctags = IClusterTags(root, {})
        return ctags.get(self.cluster, ())

    @tags.setter
    def tags(self, value):
        request = get_current_request()
        root = find_root(request.context)
        ctags = IClusterTags(root, None)
        assert self.cluster
        if ctags is not None:
            ctags[self.cluster] = value


def update_siblings(context, event):
    root = find_root(context)
    ctags = IClusterTags(root, None)
    if ctags is None:
        return
    for docid in root.catalog.search(cluster = context.cluster)[1]:
        path = root.document_map.address_for_docid(docid)
        obj = find_resource(root, path)
        if obj == context:
            continue
        ICataloger(obj).index_object()

def remove_tags_on_last_obj_delete(context, event):
    root = find_root(context)
    for docid in root.catalog.search(cluster = context.cluster)[1]:
        path = root.document_map.address_for_docid(docid)
        obj = find_resource(root, path)
        if obj != context:
            return
    #This point should never be reached if other items exist
    ctags = IClusterTags(root, {})
    ctags.pop(context.cluster, None)

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
def deferred_lang_widget(node, kw):
    request = kw['request']
    if request.GET.get('language', None):
        return deform.widget.HiddenWidget()
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
    config.add_subscriber(update_siblings, [IQuestion, IObjectAddedEvent])
    config.add_subscriber(update_siblings, [IQuestion, IObjectUpdatedEvent])
    config.add_subscriber(remove_tags_on_last_obj_delete, [IQuestion, IObjectWillBeRemovedEvent])
    config.add_content_factory(Question)
    config.add_addable_content("Question", "Questions")
    config.add_content_schema('Question', QuestionSchema, 'edit')
    config.add_content_schema('Question', QuestionSchema, 'add')
    config.add_content_schema('Question', QuestionSchema, 'view')

