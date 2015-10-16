from pyramid.view import view_config
from arche.interfaces import IRoot
from arche.security import PERM_VIEW
from arche.views.base import BaseView
from arche_m2m.interfaces import IOrganisation


@view_config(context = IRoot,
             permission = PERM_VIEW,
             renderer = 'arche_m2m:templates/site.pt')
class SiteHomeView(BaseView):

    def __call__(self):
        organisations = [x for x in self.context.values() if IOrganisation.providedBy(x) and self.request.has_permission(PERM_VIEW, x)]
        organisations = sorted(organisations, key = lambda x: x.title.lower())
        return {'organisations': organisations}
