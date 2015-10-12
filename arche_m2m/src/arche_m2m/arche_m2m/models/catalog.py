# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from repoze.catalog.indexes.field import CatalogFieldIndex

from arche_m2m.interfaces import IQuestion


def cluster_indexer(context, default):
    res = getattr(context, 'cluster', None)
    return res and res or default

def language_indexer(context, default):
    res = getattr(context, 'language', None)
    return res and res or default

def question_type_indexer(context, default):
    if IQuestion.providedBy(context):
        res = getattr(context, 'question_type', None)
        return res and res or default
    return default


def includeme(config):
    m2m_indexes = {
        'cluster': CatalogFieldIndex(cluster_indexer),
        'language': CatalogFieldIndex(language_indexer),
        'question_type': CatalogFieldIndex(question_type_indexer),
        }
    config.add_catalog_indexes(__name__, m2m_indexes)
