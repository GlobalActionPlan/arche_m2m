import colander
import deform
from arche import security
from arche.views.base import BaseForm
from arche.views.base import BaseView
from arche.views.base import DefaultEditForm
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import resource_path
from pyramid.view import view_config

from arche_m2m import _
from arche_m2m.interfaces import IChoice
from arche_m2m.interfaces import IQuestion
from arche_m2m.interfaces import IQuestionType
from arche_m2m.interfaces import IQuestionTypes
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import IQuestions


class BaseQuestionMixin(object):
    """ Mixin for Question and QuestionType views.
    """

    @reify
    def languages(self):
        return self.request.registry.settings.get('m2m.languages', 'en').split()

    @reify
    def other_langs(self):
        langs = list(self.languages)
        if self.request.locale_name in langs:
            langs.remove(self.request.locale_name)
        return langs

    @reify
    def question_type(self):
        if IQuestionType.providedBy(self.context):
            return self.context
        return self.resolve_uid(self.context.question_type)

    @reify
    def question_widget(self):
        return self.request.registry.queryAdapter(self.question_type,
                                                  IQuestionWidget,
                                                  name = self.question_type.input_widget)

    @reify
    def allow_choices(self):
        return getattr(self.question_widget, 'allow_choices', False)

    def get_object_siblings(self, context):
        siblings = {}
        if not hasattr(context, 'cluster'):
            return siblings
        for obj in self.catalog_search(resolve = True, language = self.languages, cluster = context.cluster):
            siblings[obj.language] = obj
        return siblings

    def check_success(self, appstruct):
        self.flash_messages.add(_('Success, captured: ${appstruct}',
                                  mapping = {'appstruct': appstruct}))
        return HTTPFound(location = self.request.resource_url(self.context))


@view_config(context = IQuestionType,
             name = 'view',
             permission = security.PERM_VIEW,
             renderer = 'arche_m2m:templates/question_form.pt')
class QuestionTypePreview(BaseForm, BaseQuestionMixin):
    buttons = (deform.Button(name = 'check', css_class = 'btn btn-primary'),)

    def get_schema(self):
        schema = colander.Schema(title = _("Preview"))
        if self.question_widget:
            schema.add(self.question_widget.node(self.context.__name__))
        return schema


@view_config(context = IQuestion,
             name = 'view',
             permission = security.PERM_VIEW,
             renderer='arche_m2m:templates/question_form.pt')
class QuestionPreview(BaseForm, BaseQuestionMixin):
    buttons = (deform.Button(name = 'check', css_class = 'btn btn-primary'),)

    @reify
    def languages(self):
        langs = self.request.registry.settings.get('m2m.languages', 'en').split()
        return langs

    def get_schema(self):
        schema = colander.Schema(title = _("Preview"))
        if self.question_widget:
            schema.add(self.question_widget.node(self.context.__name__,
                                                lang = self.context.language,
                                                question = self.context,
                                                title = self.context.title))
        return schema


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

    def save_success(self, appstruct):
        self.flash_messages.add(self.default_success, type="success")
        self.context.update(**appstruct)
        return HTTPFound(location = self.request.resource_url(self.context.__parent__))

    def cancel(self, *args):
        return HTTPFound(location=self.request.resource_url(self.context.__parent__))
    cancel_success = cancel_failure = cancel


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

    @reify
    def languages(self):
        langs = self.request.registry.settings.get('m2m.languages', 'en').split()
        return langs

    def __call__(self):
        return {}
