from __future__ import unicode_literals

from BTrees.OOBTree import OOBTree
from arche.api import Content
from arche.schemas import tagging_widget
from zope.interface import implementer
import colander
#import deform

from arche_m2m import _
from arche_m2m.interfaces import IOrganisation


@implementer(IOrganisation)
class Organisation(Content):
    type_title = _("Organisation")
    type_name = "Organisation"
    add_permission = "Add %s" % type_name
    nav_visible = True
    listing_visible = True
    search_visible = True

    def __init__(self, **kw):
        super(self, Organisation).__init__(**kw)
        self.variants = OOBTree()

    

class OrganisationSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))
    tags = colander.SchemaNode(colander.List(),
                               title = _("Tags"),
                               missing = "",
                               widget = tagging_widget)


def includeme(config):
    config.add_content_factory(Organisation)
    config.add_addable_content("Organisation", ("Root",))
    config.add_content_schema('Organisation', OrganisationSchema, 'edit')
    config.add_content_schema('Organisation', OrganisationSchema, 'add')
    config.add_content_schema('Organisation', OrganisationSchema, 'view')
