from arche.workflow import Workflow
from arche.workflow import Transition
from arche import security

from arche_m2m import _
from arche_m2m import permissions


_closed_to_open = \
    Transition(from_state = 'closed',
               to_state = 'open',
               permission = security.PERM_EDIT,
               title = _("Open"),
               message = _("Survey opened for participants"))

_open_to_closed = \
    Transition(from_state = 'open',
               to_state = 'closed',
               permission = security.PERM_EDIT,
               title = _("Closed"),
               message = _("Now closed for new participants"))


class SurveyWorkflow(Workflow):
    """ To manage states for surveys"""
    name = 'survey_workflow'
    title = _("Survey workflow")
    states = {'open': _("Open"),
              'closed': _("Closed")}
    transitions = {_closed_to_open.name: _closed_to_open,
                   _open_to_closed.name: _open_to_closed}
    initial_state = 'closed'

    @classmethod
    def init_acl(cls, registry):
        acl_reg = security.get_acl_registry(registry)
        open_name = "%s:open" % cls.name
        acl_reg[open_name] = security.ACLEntry()
        acl_reg[open_name].add(security.ROLE_ADMIN, security.ALL_PERMISSIONS)
        acl_reg[open_name].add(security.ROLE_EDITOR,
                               [security.PERM_VIEW, security.PERM_EDIT, "Add SurveySection"])
        acl_reg[open_name].add(security.ROLE_VIEWER, [security.PERM_VIEW])
        acl_reg[open_name].add(security.Everyone, [permissions.PARTICIPATE_SURVEY])
        closed_name = "%s:closed" % cls.name
        acl_reg[closed_name] = security.ACLEntry()
        acl_reg[closed_name].add(security.ROLE_ADMIN, security.ALL_PERMISSIONS)
        acl_reg[closed_name].add(security.ROLE_EDITOR,
                                 [security.PERM_VIEW, security.PERM_EDIT, "Add SurveySection"])
        acl_reg[closed_name].add(security.ROLE_VIEWER, [security.PERM_VIEW])


def includeme(config):
    config.add_workflow(SurveyWorkflow)
    config.set_content_workflow('Survey', 'survey_workflow')
