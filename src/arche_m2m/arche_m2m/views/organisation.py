from __future__ import unicode_literals

from arche import security
from arche.views.base import BaseView
from pyramid.view import view_config

from arche_m2m import _
from arche_m2m.interfaces import IOrganisation


@view_config(name='view',
             context=IOrganisation,
             renderer='arche_m2m:templates/organisation.pt',
             permission=security.PERM_VIEW)
class OrganisationView(BaseView):

    def __call__(self):
        return {}
