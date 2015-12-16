from __future__ import unicode_literals

from arche.schemas import tagging_widget
import colander

from arche_m2m import _


class OrganisationSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))
    tags = colander.SchemaNode(colander.List(),
                               title = _("Tags"),
                               missing = "",
                               widget = tagging_widget)


def includeme(config):
    config.add_content_schema('Organisation', OrganisationSchema, ('edit', 'add', 'view'))
