from __future__ import unicode_literals

import colander
import deform
from zope.component import adapter
from zope.interface import implementer

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

    def __init__(self, context):
        self.context = context

    def node(self, name, lang = None, **kwargs):
        #kw = copy(self.default_kwargs)
        kw = {}
        kw['name'] = name
        kw['title'] = self.context.title
        kw['widget'] = self.widget()
        kw.update(kwargs)
        return colander.SchemaNode(self.data_type, **kw)

    def widget(self, **kw):
        raise NotImplementedError()


class TextWidget(QuestionWidget):
    name = "text_widget"
    title = _(u"Text string")

    def widget(self, **kw):
        return deform.widget.TextInputWidget(**kw)


class RadioChoiceWidget(QuestionWidget):
    name = "radio_choice_widget"
    title = _(u"Radio choice")

    def widget(self, **kw):
        #FIXME: Lang!
        choices = [(name, choice.title) for (name, choice) in self.context.items()]
        return deform.widget.RadioChoiceWidget(values = choices)


# class BaseQuestionType(BaseFolder, SecurityAware):
#     """ See interfaces for docs """
#     implements(IQuestionType)
#     allowed_contexts = ('QuestionTypes',)
#     uid_name = True
#     go_to_after_add = u'edit'
#
#     @property
#     def widget(self):
#         widget_name = self.get_field_value('input_widget', '')
#         return queryAdapter(self, IQuestionWidget, name = widget_name)
#
#     @property
#     def default_kwargs(self):
#         return self.get_field_value('default_kwargs', {})
#
#     @default_kwargs.setter
#     def default_kwargs(self, value):
#         self.set_field_value('default_kwargs', dict(value))
#
#     @property
#     def description(self):
#         return self.get_field_value('description', u'')
#
#     def node(self, name, lang = None, **kwargs):
#         kw = copy(self.default_kwargs)
#         kw['name'] = name
#         if self.widget:
#             kw['widget'] = self.widget(lang = lang)
#         kw.update(kwargs)
#         return colander.SchemaNode(colander.String(), **kw)
#
#     def count_occurences(self, data):
#         results = OOBTree()
#         for item in data:
#             if item not in results:
#                 results[item] = 1
#             else:
#                 results[item]+=1
#         return results
#
#     def __repr__(self): # pragma: no cover
#         return "<%s '%s'>" % (self.__class__.__module__, self.title)
#
#     def render_result(self, request, data):
#         response = {'data':data,}
#         return render('../views/templates/results/basic.pt', response, request=request)
#
#     def csv_header(self):
#         return [self.title]
#
#     def csv_export(self, data):
#         response = []
#         for reply in data:
#             if isinstance(reply, basestring):
#                 response.append(['', reply.encode('utf-8')])
#             else:
#                 response.append(['', reply])
#         return response
#
#     def check_safe_delete(self, request):
#         root = find_root(self)
#         results = root['questions'].questions_by_type(self.__name__)
#         if not results:
#             return True
#         #FIXME: Only flash messages can handle html right now
#         out = u"<br/><br/>"
#         rurl = request.resource_url
#         out += ",<br/>".join([u'<a href="%s">%s</a>' % (rurl(x), x.title) for x in results])
#         request.session.flash(_(u"Can't delete this since it's used in: ${out}",
#                                 mapping = {'out': out}))
#         return False
#
#
# @content_factory('TextQuestionType')
# class TextQuestionType(BaseQuestionType):
#     implements(ITextQuestionType)
#     content_type = u'TextQuestionType'
#     display_name = _(u"Text question")
#     schemas = {'add': 'AddQuestionTypeSchema', 'edit': 'EditTextQuestionSchema', 'delete': 'DeleteQuestionTypeSchema'}





# class NumberWidget(BaseQuestionWidget):
#     name = u'number_widget'
#     title = _(u"Number field")
#     adapts(IQuestionType)
#
#     def __call__(self, **kw):
#         return deform.widget.TextInputWidget()
#
#
# class TextAreaWidget(BaseQuestionWidget):
#     name = u'text_area_widget'
#     title = _(u"Text area")
#     adapts(IQuestionType)
#
#     def __call__(self, **kw):
#         return deform.widget.TextAreaWidget(cols = 60, rows = 10)
#
#
# class RadioWidget(BaseQuestionWidget):
#     name = u'radio_widget'
#     title = _(u"Radio choice")
#     adapts(IQuestionType)
#
#     def __call__(self, **kw):
#         lang = kw.get('lang', None)
#         choices = [(name, choice.get_title(lang = lang)) for (name, choice) in self.context.items()]
#         return deform.widget.RadioChoiceWidget(values=choices)
#
#
# class DropdownWidget(BaseQuestionWidget):
#     name = u'dropdown_widget'
#     title = _(u"Dropdown choice")
#     adapts(IQuestionType)
#
#     def __call__(self, **kw):
#         lang = kw.get('lang', None)
#         choices = [('', _(u"<Select>"))]
#         choices.extend([(name, choice.get_title(lang = lang)) for (name, choice) in self.context.items()])
#         return deform.widget.SelectWidget(values=choices)
#
#
# class CheckboxWidget(BaseQuestionWidget):
#     name = u"checkbox_widget"
#     title = _(u"Checkbox multichoice")
#     adapts(IQuestionType)
#
#     def __call__(self, **kw):
#         lang = kw.get('lang', None)
#         choices = []
#         choices.extend([(name, choice.get_title(lang = lang)) for (name, choice) in self.context.items()])
#         return deform.widget.CheckboxChoiceWidget(values=choices)


def includeme(config):
    config.registry.registerAdapter(TextWidget, name = TextWidget.name)
    config.registry.registerAdapter(RadioChoiceWidget, name = RadioChoiceWidget.name)
    # config.registry.registerAdapter(TextWidget, name = TextWidget.name)
    # config.registry.registerAdapter(NumberWidget, name = NumberWidget.name)
    # config.registry.registerAdapter(TextAreaWidget, name = TextAreaWidget.name)
    # config.registry.registerAdapter(RadioWidget, name = RadioWidget.name)
    # config.registry.registerAdapter(DropdownWidget, name = DropdownWidget.name)
    # config.registry.registerAdapter(CheckboxWidget, name = CheckboxWidget.name)
