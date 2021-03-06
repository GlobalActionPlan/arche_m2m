from __future__ import unicode_literals

from arche import security
from arche.views.base import BaseView
from pyramid.view import view_config

from arche_m2m import _
from arche_m2m.interfaces import IOrganisation
from arche_m2m.interfaces import IQuestions
from arche_m2m.interfaces import ISurvey


@view_config(name='view',
             context=IOrganisation,
             renderer='arche_m2m:templates/organisation.pt',
             permission=security.PERM_VIEW)
class OrganisationView(BaseView):

    def __call__(self):
        surveys = []
        questions = []
        for obj in self.context.values():
            if not self.request.has_permission(security.PERM_VIEW, obj):
                continue
            if ISurvey.providedBy(obj):
                surveys.append(obj)
            elif IQuestions.providedBy(obj):
                questions.append(obj)
        return {'surveys': surveys, 'questions': questions}
