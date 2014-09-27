from __future__ import unicode_literals

from BTrees.OOBTree import OOBTree
from arche import security
from arche.api import Content
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from zope.interface import implementer
import colander

from arche_m2m import _
from arche_m2m.interfaces import IQuestionnaire


@implementer(IQuestionnaire)
class Questionnaire(Content):
    type_title = _("Questionnaire")
    type_name = "Questionnaire"
    add_permission = "Add %s" % type_name
#    default_view = u"view"
    nav_visible = True
    listing_visible = True
    search_visible = True

    def __init__(self, **kwargs):
        self.responses = OOBTree()
        super(Questionnaire, self).__init__(**kwargs) #BaseMixin!

    @property
    def question_ids(self): return getattr(self, '__question_ids__', ())
    @question_ids.setter
    def question_ids(self, value): self.__question_ids__ = tuple(value)

    def get_questions(self, lang, resolve = False):
        root = find_root(self)
        docids = []
        results = []
        for qid in self.question_ids:
            for docid in root.catalog.search(cluster = qid, language = lang)[1]:
                docids.append(docid)
        if resolve:
            request = get_current_request()
            for docid in docids:
                path = root.document_map.address_for_docid(docid)
                obj = find_resource(root, path)
                if request.has_permission(security.PERM_VIEW, obj):
                    results.append(obj)
        return resolve and results or docids


class QuestionnaireSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))


def includeme(config):
    config.add_content_factory(Questionnaire)
    config.add_addable_content("Questionnaire", "Survey")
    config.add_content_schema('Questionnaire', QuestionnaireSchema, 'edit')
    config.add_content_schema('Questionnaire', QuestionnaireSchema, 'add')
