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
from arche_m2m.interfaces import ISurveySection
from arche_m2m.models.i18n import TranslationMixin
from arche_m2m.models.i18n import deferred_translations_node
import deform


@implementer(ISurveySection)
class SurveySection(Content, TranslationMixin):
    type_title = _("Survey section")
    type_name = "SurveySection"
    add_permission = "Add %s" % type_name
    nav_visible = True
    listing_visible = True
    search_visible = True
    body = ""

    def __init__(self, **kwargs):
        self.responses = OOBTree()
        super(SurveySection, self).__init__(**kwargs) #BaseMixin!

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
                results.append(obj)
        return resolve and results or docids


    """ New function """
    def get_question_id(self,lang):
        """
            I created this function to recup the ids of questions. And it return a list of this Ids. I think the order of id in the list
            is correct.
        """
        root = find_root(self)
        list_id=[] # list of id
        for qid in self.question_ids:
            for docid in root.catalog.search(cluster=qid,language=lang)[1]:
                list_id.append(docid)
        return list_id


class SurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"),
                                translate = True,
                                translate_missing = "")
    body = colander.SchemaNode(colander.String(),
                                title = _("Body"),
                                widget = deform.widget.RichTextWidget(),
                                translate = True,
                                translate_missing = "")
    translations = deferred_translations_node


def includeme(config):
    config.add_content_factory(SurveySection, addable_to = ("Survey",))
    config.add_content_schema('SurveySection', SurveySectionSchema, 'edit')
    config.add_content_schema('SurveySection', SurveySectionSchema, 'add')
