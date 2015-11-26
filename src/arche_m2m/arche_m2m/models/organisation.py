from __future__ import unicode_literals

from BTrees.OOBTree import OOBTree
from arche.api import Content
from arche.api import ContextACLMixin
from arche.api import LocalRolesMixin
from arche.schemas import tagging_widget
from arche_m2m.models.question import deferred_question_type_widget
from zope.interface import implementer
from pyramid.traversal import resource_path
import colander
import deform

from arche_m2m import _
from arche_m2m.interfaces import IOrganisation


@implementer(IOrganisation)
class Organisation(Content, LocalRolesMixin, ContextACLMixin):
    type_title = _("Organisation")
    type_name = "Organisation"
    add_permission = "Add %s" % type_name
    _referenced_questions = frozenset()
    nav_visible = False
    listing_visible = True
    search_visible = True

    def __init__(self, **kw):
        super(Organisation, self).__init__(**kw)
        self.variants = OOBTree()

    @property
    def referenced_questions(self):
        return self._referenced_questions
    @referenced_questions.setter
    def referenced_questions(self, value):
        self._referenced_questions = frozenset(value)

@colander.deferred
def referenced_questions_widget(node, kw):
    view = kw['view']
    query = "type_name == 'Questions'"
    values = []
    for obj in view.catalog_query(query, resolve = True, sort_index = 'sortable_title'):
        values.append((obj.uid, "%s (%s)" % (obj.title, resource_path(obj))))
    return deform.widget.CheckboxChoiceWidget(values = values)

class OrganisationSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _("Title"))
    tags = colander.SchemaNode(colander.List(),
                               title = _("Tags"),
                               missing = "",
                               widget = tagging_widget)
    referenced_questions = colander.SchemaNode(colander.Set(),
                                                title = _("Question sets to work with"),
                                                widget = referenced_questions_widget)

def includeme(config):
    config.add_content_factory(Organisation)
    config.add_addable_content("Organisation", ("Root",))
    config.add_content_schema('Organisation', OrganisationSchema, 'edit')
    config.add_content_schema('Organisation', OrganisationSchema, 'add')
    config.add_content_schema('Organisation', OrganisationSchema, 'view')
