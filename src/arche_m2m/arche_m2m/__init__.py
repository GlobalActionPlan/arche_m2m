from arche.populators import Populator
from arche.security import ROLE_EDITOR
from arche.security import get_acl_registry
from arche.utils import get_content_factories
from pyramid.i18n import TranslationStringFactory
from repoze.catalog.indexes.field import CatalogFieldIndex

_ = TranslationStringFactory('arche_m2m')


def cluster_indexer(context, default):
    res = getattr(context, 'cluster', None)
    return res and res or default

def language_indexer(context, default):
    res = getattr(context, 'language', None)
    return res and res or default


class M2MPopulator(Populator):
    name = "m2m_populator"
    title = "Made to Measure"
    description = "Installs made to measure"

    def populate(self, **kw):
        self.context.catalog['cluster'] = CatalogFieldIndex(cluster_indexer)
        self.context.catalog['language'] = CatalogFieldIndex(language_indexer)


def includeme(config):
    config.include('.models')
    config.include('.views')
    config.add_translation_dirs('arche_m2m:locale')
    config.add_populator(M2MPopulator)
    #Adjusting add perms to all Editors is kind of reckless. This will probably change in Arche.
    factories = get_content_factories(config.registry)
    add_perms = []
    for factory in factories.values():
        if hasattr(factory, 'add_permission'):
            add_perms.append(factory.add_permission)
    aclreg = get_acl_registry(config.registry)
    aclreg.default.add(ROLE_EDITOR, add_perms)
