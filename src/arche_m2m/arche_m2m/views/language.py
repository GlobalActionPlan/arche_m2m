from arche.interfaces import IRoot
from arche.views.base import BaseView
from betahaus.viewcomponent.decorators import view_action
from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.traversal import find_root
from pyramid.view import view_config

from arche_m2m import _


class LanguageView(BaseView):

    @view_config(name = 'set_language', context = IRoot, permission = NO_PERMISSION_REQUIRED)
    def set_language(self):
        lang = self.request.GET.get('lang', None)
        msg = _(u"Language set to ${selected_lang}",
                mapping = {'selected_lang': lang})
                #mapping = {'selected_lang': self.trans_util.title_for_code(lang)})
        self.flash_messages.add(msg)
        self.request.response.set_cookie('_LOCALE_', value = lang)
        url = self.request.GET.get('return_url', self.request.resource_url(self.root))
        return HTTPFound(location = url, headers = self.request.response.headers)


@view_action('actions_menu', 'set_language',
             priority = 50)
def set_language_action(context, request, va, **kw):
    out = """<li role="presentation" class="dropdown-header">%s</li>\n""" % _("Language")
    languages = [(x, x) for x in request.registry.settings.get('m2m.languages', 'en').split()]
    #FIXME: lang titles
    root = find_root(context)
    for (name, title) in languages:
        selected = ""
        if request.locale_name == name:
            selected = """<span class="glyphicon glyphicon-ok pull-right"></span>"""
        out += """<li><a href="%(url)s">%(title)s %(selected)s</a></li>""" %\
                {'url': request.resource_url(root, 'set_language', query = {'lang': name, 'return_url': request.url}),
                 'title': title,
                 'selected': selected}
    return out
