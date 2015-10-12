from arche import security
from arche.views.base import BaseView
from pyramid.view import view_config

from arche_m2m.interfaces import ISurvey
from arche_m2m.interfaces import ISurveySection


class TranslateView(BaseView):

    @view_config(context = ISurveySection,
                 name = "translate_questions",
                 permission = security.PERM_EDIT,
                 renderer = "arche_m2m:templates/survey_translate_questions.pt")
    def translate_questions_view(self):
        to_lang = self.request.GET.get('to_lang', None)
        to_lang_questions = {}
        for obj in self.context.get_questions(to_lang, resolve = True):
            to_lang_questions[obj.cluster] = obj
        return {'to_lang': to_lang, 'to_lang_questions': to_lang_questions}
