import csv

from arche import security
from arche.views.base import BaseView
from pyramid.httpexceptions import HTTPForbidden
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import view_defaults
from six import StringIO

from arche_m2m import _
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import ISurvey
from arche_m2m.interfaces import ISurveySection


@view_defaults(context = ISurvey, permission = security.PERM_VIEW)
class ExportView(BaseView):

    @view_config(name = 'export.csv')
    def csv(self):
        output = StringIO()
        lang_name = self.request.locale_name
        writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, dialect = csv.excel)
        writer.writerow([self.context.title.encode('utf-8')])
        writer.writerow([_('Export using language:'), lang_name])
        
        langs = self.context.languages
        lrow = [_("Survey languages").encode('utf-8')]
        for lang in langs:
            lrow.append(lang)
        writer.writerow(lrow)

        writer.writerow([])

        for section in self.context.values():
            if not ISurveySection.providedBy(section):
                continue
            writer.writerow([])
            writer.writerow([_('Section:'), section.title.encode('utf-8')])
            writer.writerow([_('Responses:'), len(section.responses)])
            writer.writerow([])

            for question in section.get_questions(lang_name, resolve = True):
                question_type = self.resolve_uid(question.question_type, perm = None)
                if not question_type:
                    raise HTTPForbidden("%r has no question type set." % question)
                question_widget = self.request.registry.queryAdapter(question_type,
                                                                     IQuestionWidget,
                                                                     name = getattr(question_type, 'input_widget', ''))
                if not question_widget:
                    raise HTTPForbidden("%r has no question widget set." % question_type)
                response = question_widget.responses(section, question)
                writer.writerow([question.title.encode('utf-8')])
                #Choice responses
                if isinstance(response, dict):
                    choices = dict([(choice.cluster, choice.title.encode('utf-8')) for choice in question_type.get_choices(lang_name)])
                    choices.update([(choice.cluster, choice.title.encode('utf-8')) for choice in question.get_choices(lang_name)])
                    results = dict([(x, 0) for x in choices])
                    results.update(response)
                    for (k, v) in results.items():
                        writer.writerow([choices.get(k, k), v])
                #Text, number etc
                else:
                    [writer.writerow([x]) for x in response]
                writer.writerow([])
        contents = output.getvalue()
        output.close()
        return Response(content_type = 'text/csv', body = contents)
