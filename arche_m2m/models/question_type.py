from __future__ import unicode_literals

from pyramid.httpexceptions import HTTPForbidden

from arche.api import Base
from arche.api import Content
from arche.interfaces import IIndexedContent
from arche.interfaces import IObjectAddedEvent
from zope.interface import implementer

from arche_m2m import _
from arche_m2m.interfaces import IChoice
from arche_m2m.interfaces import IQuestionType


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

def choice_language_guard(context, event):
    parent_lang = getattr(context.__parent__, 'language', None)
    if parent_lang and parent_lang != context.language:
        raise HTTPForbidden(_("It's not possible to add choices with language "
                              "'${choice_lang}' to a parent with the language '${parent_lang}'.",
                              mapping = {'choice_lang': context.language,
                                         'parent_lang': parent_lang}))

def includeme(config):
    config.add_content_factory(QuestionType, addable_to = 'QuestionTypes')
    config.add_content_factory(Choice, addable_to = ('QuestionType', 'Question'))
    config.add_subscriber(choice_language_guard, [IChoice, IObjectAddedEvent])
