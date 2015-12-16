from __future__ import unicode_literals

import colander

from arche_m2m import _


class QuestionTypesSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))


def includeme(config):
    config.add_content_schema('QuestionTypes', QuestionTypesSchema, ('edit', 'add'))
