from __future__ import unicode_literals

import colander
import deform

from arche_m2m import _
from arche_m2m.models.i18n import deferred_translations_node


class TextSectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                translate = True,
                                translate_missing = "",
                                title = _("Title"))
    body = colander.SchemaNode(colander.String(),
                                title = _("Body"),
                                widget = deform.widget.RichTextWidget(),
                                translate = True,
                                translate_missing = "")
    translations = deferred_translations_node



def includeme(config):
    config.add_content_schema('TextSection', TextSectionSchema, ('edit','add'))
