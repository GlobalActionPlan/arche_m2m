from pyramid.view import view_config
from arche import security
from arche.views.base import BaseForm, DefaultEditForm
from arche.views.base import BaseView
from pyramid.decorator import reify
from pyramid.traversal import resource_path
import colander

from arche_m2m import _
from arche_m2m.interfaces import IChoice
from arche_m2m.interfaces import IQuestion
from arche_m2m.interfaces import IQuestions
from arche_m2m.interfaces import IQuestionType
from arche_m2m.interfaces import IQuestionTypes
from arche_m2m.interfaces import IQuestionWidget


@view_config(context = IQuestion,
             name = 'view',
             permission = security.PERM_VIEW,
             renderer='arche_m2m:templates/translations_form.pt')
class QuestionPreview(BaseForm):
    buttons = ()

    @reify
    def languages(self):
        langs = self.request.registry.settings.get('m2m.languages', 'en').split()
        return langs

    def __call__(self):
        self.schema = colander.Schema(title = _("Preview"))
        question_type = self.resolve_uid(self.context.question_type)
        question_widget = self.request.registry.queryAdapter(question_type,
                                                             IQuestionWidget,
                                                             name = getattr(question_type, 'input_widget', ''))
        if question_widget:
            self.schema.add(question_widget.node(self.context.__name__, title = self.context.title))
        result = super(BaseForm, self).__call__()
        return result

    def get_siblings(self):
        siblings = {}
        for obj in self.catalog_search(resolve = True, language = self.languages, cluster = self.context.cluster):
            siblings[obj.language] = obj
        return siblings


@view_config(context = IChoice,
             permission = security.PERM_VIEW,
             renderer='arche_m2m:templates/translations_form.pt')
class ChoiceView(DefaultEditForm):

    @reify
    def languages(self):
        langs = self.request.registry.settings.get('m2m.languages', 'en').split()
        return langs

    def get_siblings(self):
        siblings = {}
        for obj in self.catalog_search(resolve = True, language = self.languages, cluster = self.context.cluster):
            siblings[obj.language] = obj
        return siblings


@view_config(context = IQuestionType,
             name = 'view',
             permission = security.PERM_VIEW,
             renderer = 'arche:templates/form.pt')
class QuestionTypePreview(BaseForm):
    buttons = ()

    def __call__(self):
        self.schema = colander.Schema(title = _("Preview"))
        question_widget = self.request.registry.queryAdapter(self.context,
                                                             IQuestionWidget,
                                                             name = self.context.input_widget)
        if question_widget:
            self.schema.add(question_widget.node(self.context.__name__))
        result = super(BaseForm, self).__call__()
        return result


@view_config(context = IQuestions,
             name = 'view',
             permission = security.PERM_VIEW,
             renderer = 'arche_m2m:templates/questions.pt')
class QuestionsView(BaseView):

    def __call__(self):
        return {}

    def get_current_questions(self):
        path = resource_path(self.context)
        return self.catalog_search(resolve = True, language = self.request.locale_name, path = path, type_name = 'Question')

    def get_siblings(self, question):
        languages = self.request.registry.settings.get('m2m.languages', 'en').split()
        if question.language in languages:
            languages.remove(question.language)
        return self.catalog_search(resolve = True, language = languages, cluster = question.cluster)


@view_config(context = IQuestionTypes,
             name = 'view',
             permission = security.PERM_VIEW,
             renderer = 'arche_m2m:templates/question_types.pt')
class QuestionTypesView(BaseView):

    def __call__(self):
        return {}
