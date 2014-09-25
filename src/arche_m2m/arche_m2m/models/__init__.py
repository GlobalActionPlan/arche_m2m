def includeme(config):
    config.include('.question')
    config.include('.question_type')
    config.include('.question_types')
    config.include('.question_widgets')
    config.include('.questionnaire')
    config.include('.questions')
    config.include('.survey')

    from arche.security import get_acl_registry
    from arche.utils import get_content_factories
    from arche.security import ROLE_ADMIN
    acl_reg = get_acl_registry(config.registry)
    factories = get_content_factories(config.registry)
    add_perms = []
    for factory in factories.values():
        if hasattr(factory, 'add_permission'):
            add_perms.append(factory.add_permission)
    acl_reg.default.add(ROLE_ADMIN, add_perms)
