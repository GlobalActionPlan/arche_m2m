from arche.views.base import BaseView
from pyramid.view import view_config

from arche_m2m.interfaces import IOrganisation
from arche_m2m import _


@view_config(context = IOrganisation, name = 'variant', renderer = 'arche_m2m:templates/modal_form.pt')
class VariantForm(BaseView):

    def __call__(self):
        uid = self.request.GET['uid']
        question = self.resolve_uid(uid)
        if 'variant' in self.request.POST:
            value = self.request.POST['variant']
            if not value or value == question.title:
                if uid in self.context.variants:
                    del self.context.variants[uid]
            else:
                self.context.variants[uid] = value
        else:
            value = self.context.variants.get(uid, question.title)
        return {'value': value}
