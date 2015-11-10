from __future__ import unicode_literals

from arche import security
from arche.utils import get_content_factories


PARTICIPATE_SURVEY = "Participate survey"


def includeme(config):
    #Adjusting add perms to all Editors is kind of reckless. This will probably change in Arche.
    acl_reg = config.registry.acl
    factories = get_content_factories(config.registry)
    add_perms = []
    for factory in factories.values():
        if hasattr(factory, 'add_permission'):
            add_perms.append(factory.add_permission)
    #Root perms
    del acl_reg['Root']
    root_acl = acl_reg.new_acl('Root')
    root_acl.add(security.ROLE_ADMIN, security.ALL_PERMISSIONS)
    root_acl.add(security.ROLE_EDITOR, add_perms)
    root_acl.add(security.ROLE_AUTHENTICATED, security.PERM_VIEW)
    #Org perms
    org_acl = acl_reg.new_acl('Organisation')
    org_acl.add(security.ROLE_ADMIN, security.ALL_PERMISSIONS)
    org_acl.add(security.ROLE_EDITOR, add_perms)
    org_acl.add(security.ROLE_EDITOR, (security.PERM_VIEW, security.PERM_EDIT))
    org_acl.add(security.ROLE_VIEWER, security.PERM_VIEW)
