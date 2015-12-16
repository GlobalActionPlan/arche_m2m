from pyramid.view import view_config, view_defaults
from arche.security import PERM_VIEW
from arche.security import NO_PERMISSION_REQUIRED
import colander
from pyramid.httpexceptions import HTTPFound
from arche.views.base import BaseView

from arche_m2m.interfaces import ITextSection
from arche_m2m.views.survey import BaseSurveySection


@view_config(context = ITextSection,
             name = 'info_panel',
             permission = PERM_VIEW,
             renderer = 'arche_m2m:templates/snippets/text_section_info_panel.pt')
class TextSectionInfoPanel(BaseView):

    __call__ = lambda x: {}


@view_defaults(context = ITextSection, renderer = 'arche_m2m:templates/text_section.pt')
class TextSectionView(BaseSurveySection):

    @property
    def main_tpl(self):
        if self.show_manager_controls:
            return 'arche:templates/master.pt'
        return 'arche_m2m:templates/master_stripped.pt'


    @view_config(name = 'view', permission = PERM_VIEW)
    def manager(self):
        response = super(TextSectionView, self).__call__()
        return response

    @view_config(permission = NO_PERMISSION_REQUIRED)
    def participant(self):
        response = super(TextSectionView, self).__call__()
        return response

    def get_schema(self):
        return colander.Schema()

    def next_success(self, appstruct):
        next_section = self.next_section()
        #Do stuff if finished
        if not next_section:
            return HTTPFound(location = self.link(self.context.__parent__, 'done'))
        view = self.show_manager_controls and 'view' or ''
        return HTTPFound(location = self.link(next_section, view))

    def previous_success(self, appstruct):
        return self.go_previous()

    def go_previous(self, *args):
        previous = self.previous_section()
        if previous is None:
            return HTTPFound(location = self.link(self.context.__parent__, 'do'))
        view = self.show_manager_controls and 'view' or ''
        return HTTPFound(location = self.link(previous, view))

    previous_failure = go_previous
