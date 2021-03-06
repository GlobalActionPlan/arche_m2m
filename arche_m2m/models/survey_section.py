from __future__ import unicode_literals

from BTrees.OOBTree import OOBTree
from arche.api import Content
from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from zope.interface import implementer

from arche_m2m import _
from arche_m2m.interfaces import ISurveySection
from arche_m2m.models.i18n import TranslationMixin


@implementer(ISurveySection)
class SurveySection(Content, TranslationMixin):
    type_title = _("Survey section")
    type_name = "SurveySection"
    add_permission = "Add %s" % type_name
    nav_visible = True
    listing_visible = True
    search_visible = True
    body = ""
    __question_ids__ = ()

    def __init__(self, **kwargs):
        self.responses = OOBTree()
        super(SurveySection, self).__init__(**kwargs) #BaseMixin!

    @property
    def question_ids(self): return getattr(self, '__question_ids__', ())
    @question_ids.setter
    def question_ids(self, value):
        value = tuple(value)
        if len(value) != len(set(value)):
            raise ValueError("question_ids contained the same value several times.")
        self.__question_ids__ = value

    def get_questions(self, lang, resolve = False):
        root = find_root(self)
        docids = []
        results = []
        for qid in self.question_ids:
            for docid in root.catalog.search(cluster = qid, language = lang)[1]:
                docids.append(docid)
        if resolve:
            for docid in docids:
                path = root.document_map.address_for_docid(docid)
                obj = find_resource(root, path)
                results.append(obj)
        return resolve and results or docids


def includeme(config):
    config.add_content_factory(SurveySection, addable_to = ("Survey",))
