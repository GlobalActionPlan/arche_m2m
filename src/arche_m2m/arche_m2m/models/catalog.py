# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from repoze.catalog.indexes.field import CatalogFieldIndex


def cluster_indexer(context, default):
    res = getattr(context, 'cluster', None)
    return res and res or default

def language_indexer(context, default):
    res = getattr(context, 'language', None)
    return res and res or default


def includeme(config):
    m2m_indexes = {
        'cluster': CatalogFieldIndex(cluster_indexer),
        'language': CatalogFieldIndex(language_indexer),
        }
    config.add_catalog_indexes(__name__, m2m_indexes)
