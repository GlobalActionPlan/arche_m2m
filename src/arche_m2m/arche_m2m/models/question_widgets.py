from __future__ import unicode_literals

from pyramid.threadlocal import get_current_request
from zope.component import adapter
from zope.interface import implementer
import colander
import deform

from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import IQuestionType
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

    def __init__(self, context):
        self.context = context

    def node(self, name, lang = None, question = None, **kwargs):
        if lang is None:
            request = get_current_request()
            lang = request.locale_name
        self.question = question
        #kw = copy(self.default_kwargs)
        kw = {}
        kw['name'] = name
        kw['title'] = self.context.title
        kw['widget'] = self.widget(lang)
        kw.update(kwargs)
        return colander.SchemaNode(self.data_type, **kw)

    def widget(self, lang, **kw):
        return self.widget_factory(**kw)


class TextWidget(QuestionWidget):
    name = "text_widget"
    title = _("Text string")
    widget_factory = deform.widget.TextInputWidget


class TextAreaWidget(QuestionWidget):
    name = "text_area_widget"
    title = _("Text area (paragraph)")
    widget_factory = deform.widget.TextAreaWidget


class IntegerWidget(QuestionWidget):
    name = "int_widget"
    title = _("Integer number")
    widget_factory = deform.widget.TextInputWidget
    data_type = colander.Int()


class DecimalWidget(QuestionWidget):
    name = "decimal_widget"
    title = _("Decimal number")
    widget_factory = deform.widget.TextInputWidget
    data_type = colander.Decimal()


class RadioChoiceWidget(QuestionWidget):
    name = "radio_choice_widget"
    title = _("Radio choice")
    widget_factory = deform.widget.RadioChoiceWidget

    def widget(self, lang, **kw):
        choices = [(choice.cluster, choice.title) for choice in self.context.get_choices(lang)]
        if self.question:
            [choices.append((choice.cluster, choice.title)) for choice in self.question.get_choices(lang)]
        return self.widget_factory(values = choices)


class DropdownChoiceWidget(RadioChoiceWidget):
    name = "dropdown_choice_widget"
    title = _("Dropdown choice")
    widget_factory = deform.widget.SelectWidget


class CheckboxMultiChoiceWidget(RadioChoiceWidget):
    name = u"checkbox_multichoice_widget"
    title = _("Checkbox multichoice")
    data_type = colander.Set()
    widget_factory = deform.widget.CheckboxChoiceWidget


def includeme(config):
    config.registry.registerAdapter(TextWidget, name = TextWidget.name)
    config.registry.registerAdapter(TextAreaWidget, name = TextAreaWidget.name)
    config.registry.registerAdapter(IntegerWidget, name = IntegerWidget.name)
    config.registry.registerAdapter(DecimalWidget, name = DecimalWidget.name)
    config.registry.registerAdapter(RadioChoiceWidget, name = RadioChoiceWidget.name)
    config.registry.registerAdapter(DropdownChoiceWidget, name = DropdownChoiceWidget.name)
    config.registry.registerAdapter(CheckboxMultiChoiceWidget, name = CheckboxMultiChoiceWidget.name)
