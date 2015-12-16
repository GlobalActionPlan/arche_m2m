from __future__ import unicode_literals

from arche.api import Content
from arche.interfaces import ICataloger
from arche.interfaces import IObjectAddedEvent
from arche.interfaces import IObjectUpdatedEvent
from arche.interfaces import IObjectWillBeRemovedEvent
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from zope.interface import implementer

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


def includeme(config):
    config.add_subscriber(update_siblings, [IQuestion, IObjectAddedEvent])
    config.add_subscriber(update_siblings, [IQuestion, IObjectUpdatedEvent])
    config.add_subscriber(remove_tags_on_last_obj_delete, [IQuestion, IObjectWillBeRemovedEvent])
    config.add_content_factory(Question, addable_to = 'Questions')

