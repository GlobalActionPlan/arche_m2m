from __future__ import unicode_literals

from persistent.list import PersistentList
from zope.interface import implementer
from arche.api import Content
from BTrees.OOBTree import OOBTree
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
        self.__question_ids__ = PersistentList()
        self.responses = OOBTree()
        super(Questionnaire, self).__init__(**kwargs) #BaseMixin!

    @property
    def question_ids(self):
        return self.__question_ids__
    @question_ids.setter
    def question_ids(self, value):
        self.__question_ids__ = PersistentList(value)


class QuestionnaireSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))


def includeme(config):
    config.add_content_factory(Questionnaire)
    config.add_addable_content("Questionnaire", "Survey")
    config.add_content_schema('Questionnaire', QuestionnaireSchema, 'edit')
    config.add_content_schema('Questionnaire', QuestionnaireSchema, 'add')
