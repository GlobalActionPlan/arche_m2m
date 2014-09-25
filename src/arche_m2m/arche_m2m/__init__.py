from pyramid.i18n import TranslationStringFactory
from arche.populators import Populator
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
    config.add_populator(M2MPopulator)
