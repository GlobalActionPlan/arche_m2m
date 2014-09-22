from __future__ import unicode_literals

from zope.interface import implementer
from arche.api import Content
from arche.views.base import BaseForm
from arche import security
import colander
import deform

from arche_m2m.interfaces import IQuestion
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m import _


@implementer(IQuestion)
class Question(Content):
    type_title = _("Question")
    type_name = "Question"
    add_permission = "Add %s" % type_name
#    default_view = u"view"
    nav_visible = True
    listing_visible = True
    search_visible = True
    question_type = None

    #FIXME: Setters and getters for question_type?


@colander.deferred
def deferred_question_type_widget(node, kw):
    view = kw['view']
    choices = []
    for obj in view.catalog_search(resolve = True, type_name = 'QuestionType'):
        title = obj.description and "%s - %s" % (obj.title, obj.description) or obj.title
        choices.append((obj.uid, title))
    return deform.widget.RadioChoiceWidget(values = choices)


class QuestionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))
    question_type = colander.SchemaNode(colander.String(),
                                        title = _(u"Question type"),
                                        widget=deferred_question_type_widget,)


class QuestionPreview(BaseForm):
    buttons = ()

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


def includeme(config):
    config.add_content_factory(Question)
    config.add_addable_content("Question", "Questions")
    config.add_content_schema('Question', QuestionSchema, 'edit')
    config.add_content_schema('Question', QuestionSchema, 'add')
    config.add_content_schema('Question', QuestionSchema, 'view')
    config.add_view(QuestionPreview,
                    name='view',
                    context=IQuestion,
                    permission=security.PERM_VIEW,
                    renderer='arche:templates/form.pt')
