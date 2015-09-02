from __future__ import absolute_import

#from js.bootstrap import bootstrap
#from js.jquery import jquery
from arche.fanstatic_lib import common_js
from arche.fanstatic_lib import main_css
from fanstatic import Library
from fanstatic import Resource
from js.jqueryui import ui_sortable

lib_m2m = Library("arche_m2m", "static")

survey_manage = Resource(lib_m2m, 'survey_manage.js', depends = (common_js, ui_sortable,))
manage_css = Resource(lib_m2m, 'manage.css', depends = (main_css,))
