""" Cluster tags stored in root. They're referenced by cluster id."""
from __future__ import unicode_literals
from UserDict import IterableUserDict

from zope.component import adapter
from arche.interfaces import IRoot
from zope.interface import implementer
from BTrees.OOBTree import OOBTree

from arche_m2m.interfaces import IClusterTags


@adapter(IRoot)
@implementer(IClusterTags)
class ClusterTags(IterableUserDict):

    def __init__(self, context):
        self.context = context
        self.data = getattr(self.context, '__cluster_tags__', {})


    def __setitem__(self, key, item):
        if isinstance(self.data, dict):
            self.data = self.context.__cluster_tags__ = OOBTree()
        self.data[key] = tuple(item)
        #FIXME: Reindex all siblings?


def includeme(config):
    config.registry.registerAdapter(ClusterTags)
