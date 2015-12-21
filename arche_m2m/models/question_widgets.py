from __future__ import unicode_literals

from pyramid.threadlocal import get_current_request
from zope.component import adapter
from zope.interface import implementer
import colander
import deform

from arche_m2m.interfaces import IQuestion
from arche_m2m.interfaces import IQuestionType
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import ISurveySection
from arche_m2m import _


@implementer(IQuestionWidget)
@adapter(IQuestionType)
class QuestionWidget(object):
    name = ""
    title = ""
    description = ""
    data_type = colander.String()
    widget_factory = None
    question = None
    missing = ""
    allow_choices = False

    def __init__(self, context):
        self.context = context

    def node(self, name, lang = None, question = None, **kwargs):
        if lang is None:
            request = get_current_request()
            lang = request.locale_name
        self.question = question
        #FIXME?
        #kw = copy(self.default_kwargs)
        kw = {}
        kw['name'] = name
        kw['title'] = self.context.title
        kw['widget'] = self.widget(lang)
        if self.question and not getattr(self.question, 'required', False):
            kw['missing'] = self.missing
        kw.update(kwargs)
        return colander.SchemaNode(self.data_type, **kw)

    def widget(self, lang, **kw):
        return self.widget_factory(**kw)

    def responses(self, section, question):
        assert ISurveySection.providedBy(section), "Not a survey section"
        assert IQuestion.providedBy(question), "Not a question"
        results = []
        for response in section.responses.values():
            results.append(response.get(question.cluster, ''))
        return results


class TextWidget(QuestionWidget):
    name = "text_widget"
    title = _("Text string")
    description = _("Regular input line widget")
    widget_factory = deform.widget.TextInputWidget


class TextAreaWidget(QuestionWidget):
    name = "text_area_widget"
    title = _("Text area (paragraph)")
    widget_factory = deform.widget.TextAreaWidget


class IntegerWidget(QuestionWidget):
    name = "int_widget"
    title = _("Integer number")
    description = _("Only allows numbers")
    widget_factory = deform.widget.TextInputWidget
    data_type = colander.Int()


class DecimalWidget(QuestionWidget):
    name = "decimal_widget"
    title = _("Decimal number")
    description = _("Only allows decimals.")
    widget_factory = deform.widget.TextInputWidget
    data_type = colander.Decimal()


class RadioChoiceWidget(QuestionWidget):
    name = "radio_choice_widget"
    title = _("Radio choice")
    description = _("A choice widget with radio buttons")
    widget_factory = deform.widget.RadioChoiceWidget
    allow_choices = True

    def widget(self, lang, **kw):
        choices = [(choice.cluster, choice.title) for choice in self.context.get_choices(lang)]
        if self.question:
            for choice in self.question.get_choices(lang):
                choices.append((choice.cluster, choice.title))
        return self.widget_factory(values = choices)

    def responses(self, section, question):
        assert ISurveySection.providedBy(section), "Not a survey section"
        assert IQuestion.providedBy(question), "Not a question"
        results = {}
        for response in section.responses.values():
            val =  response.get(question.cluster, '')
            if val in results:
                results[val] += 1
            else:
                results[val] = 1
        return results


class DropdownChoiceWidget(RadioChoiceWidget):
    name = "dropdown_choice_widget"
    title = _("Dropdown choice")
    description = _("A choice widget as a dropdown menu.")
    widget_factory = deform.widget.SelectWidget
    allow_choices = True


class CheckboxMultiChoiceWidget(RadioChoiceWidget):
    name = u"checkbox_multichoice_widget"
    title = _("Checkbox multichoice")
    description = _("Allows several checkboxes to be ticked.")
    data_type = colander.Set()
    widget_factory = deform.widget.CheckboxChoiceWidget
    missing = ()
    allow_choices = True

    def responses(self, section, question):
        assert ISurveySection.providedBy(section), "Not a survey section"
        assert IQuestion.providedBy(question), "Not a question"
        results = {}
        for response in section.responses.values():
            vals =  response.get(question.cluster, '')
            for val in vals:
                if val in results:
                    results[val] += 1
                else:
                    results[val] = 1
        return results


def includeme(config):
    config.registry.registerAdapter(TextWidget, name = TextWidget.name)
    config.registry.registerAdapter(TextAreaWidget, name = TextAreaWidget.name)
    config.registry.registerAdapter(IntegerWidget, name = IntegerWidget.name)
    config.registry.registerAdapter(DecimalWidget, name = DecimalWidget.name)
    config.registry.registerAdapter(RadioChoiceWidget, name = RadioChoiceWidget.name)
    config.registry.registerAdapter(DropdownChoiceWidget, name = DropdownChoiceWidget.name)
    config.registry.registerAdapter(CheckboxMultiChoiceWidget, name = CheckboxMultiChoiceWidget.name)
