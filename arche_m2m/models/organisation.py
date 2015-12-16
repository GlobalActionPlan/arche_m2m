from __future__ import unicode_literals

from BTrees.OOBTree import OOBTree
from arche.api import Content
from arche.api import ContextACLMixin
from arche.api import LocalRolesMixin
from zope.interface import implementer

from arche_m2m import _
from arche_m2m.interfaces import IOrganisation


@implementer(IOrganisation)
class Organisation(Content, LocalRolesMixin, ContextACLMixin):
    type_title = _("Organisation")
    type_name = "Organisation"
    add_permission = "Add %s" % type_name
    nav_visible = False
    listing_visible = True
    search_visible = True

    def __init__(self, **kw):
        super(Organisation, self).__init__(**kw)
        self.variants = OOBTree()



def includeme(config):
    config.add_content_factory(Organisation)
    config.add_addable_content("Organisation", ("Root",))
