import csv

from arche import security
from arche.views.base import BaseView
from pyramid.httpexceptions import HTTPForbidden
from pyramid.response import Response
from pyramid.view import view_config
from six import StringIO

from arche_m2m import _
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import ISurvey
from arche_m2m.interfaces import ISurveySection
from arche_m2m.interfaces import IQuestion


class BaseExportView(BaseView):

    def get_sections(self):
        for obj in self.context.values():
            if ISurveySection.providedBy(obj):
                yield obj

    def get_choices(self, question):
        assert IQuestion.providedBy(question)
        question_type = self.request.get_question_type(question)
        results = [x for x in question_type.get_choices(self.request.locale_name)]
        results.extend([x for x in question.get_choices(self.request.locale_name)])
        return results

    def get_choice_sorted_questions(self, section):
        results = {}
        for question in section.get_questions(self.request.locale_name, resolve = True):
            choices = tuple([x.cluster for x in self.get_choices(question)])
            curr = results.setdefault(choices, [])
            curr.append(question)
        return results


@view_config(name = 'export.csv', context = ISurvey, permission = security.PERM_VIEW)
class CSVExport(BaseExportView):

    def __call__(self):
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
        for section in self.get_sections():
            writer.writerow([])
            writer.writerow([_('Section:'), section.title.encode('utf-8')])
            writer.writerow([_('Responses:'), len(section.responses)])
            writer.writerow([])
            for (choices, questions) in self.get_choice_sorted_questions(section).items():
                write_header = True
                for question in questions:
                    question_widget = self.request.get_question_widget(question)
                    choice_objects = self.get_choices(question)
                    if write_header:
                        row = ['']
                        for choice in choice_objects:
                            row.append(choice.title.encode('utf-8'))
                        writer.writerow(row)
                        write_header = False
                    response = question_widget.responses(section, question)
                    if isinstance(response, dict):
                        results = dict([(x, 0) for x in choices])
                        results.update(response)
                        out = [question.title.encode('utf-8')]
                        for choice in choice_objects:
                            out.append(results.get(choice.cluster))
                        writer.writerow(out)
                    else:
                        writer.writerow([])
                        writer.writerow([question.title.encode('utf-8')])
                        for x in response:
                            if x:
                                if isinstance(x, unicode):
                                    writer.writerow([x.encode('utf-8')])
                                else:
                                    writer.writerow([x])
        contents = output.getvalue()
        output.close()
        return Response(content_type = 'text/csv', body = contents)
