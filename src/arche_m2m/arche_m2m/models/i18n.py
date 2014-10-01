from __future__ import unicode_literals

from BTrees.OOBTree import OOBTree
from persistent.dict import PersistentDict
from pyramid.threadlocal import get_current_registry
import colander

from arche_m2m import _


class TranslationMixin(object):

    @property
    def languages(self):
        langs = []
        langs.extend(self.translations.keys())
        reg = get_current_registry()
        default_lang = reg.settings.get('pyramid.default_locale_name', 'en')
        if default_lang not in langs:
            langs.insert(0, default_lang)
        return langs

    @property
    def translations(self): return getattr(self, '__translations__', {})
    @translations.setter
    def translations(self, value):
        try:
            self.__translations__.clear()
        except AttributeError:
            self.__translations__ = OOBTree()
        for (lang, translatables) in value.items():
            results = {}
            for (k, v) in translatables.items():
                if v:
                    results[k] = v
            if results:
                self.__translations__[lang] = PersistentDict(results)

    def translate(self, key, lang):
        try:
            return self.translations[lang][key]
        except KeyError:
            return getattr(self, key)


@colander.deferred
def deferred_translations_node(nodes, kw):
    """ Use translate and translate_missing properties on a schema to generate
        translation subnodes.
    """
    _marker = object()
    request = kw['request']
    languages = request.registry.settings.get('m2m.languages', 'en').split()
    default_lang = request.registry.settings.get('pyramid.default_locale_name', 'en')
    if default_lang in languages:
        languages.remove(default_lang)
    if not languages:
        return
    #find translatables
    translatables = []
    for node in nodes:
        if getattr(node, 'translate', False):
            translatables.append(node.name)
    if not translatables:
        return
    schema = colander.Schema()
    schema.title = _("Translations")
    for lang in languages:
        schema[lang] = colander.Schema()
        schema[lang].title = lang
        for trans in translatables:
            clone = nodes[trans].clone()
            missing = getattr(nodes[trans], 'translate_missing', _marker)
            if missing is not _marker:
                clone.missing = missing
            schema[lang].add(clone)
    nodes['translations'] = schema
