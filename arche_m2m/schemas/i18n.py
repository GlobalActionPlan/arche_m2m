from uuid import uuid4

import colander
import deform


@colander.deferred
def deferred_cluster_id(node, kw):
    request = kw['request']
    return request.GET.get('cluster', str(uuid4()))

@colander.deferred
def deferred_lang_widget(node, kw):
    request = kw['request']
    if request.GET.get('language', None):
        return deform.widget.HiddenWidget()
    choices = []
    languages = request.registry.settings.get('m2m.languages', 'en').split()
    for lang in languages:
        choices.append((lang, lang))
    return deform.widget.SelectWidget(values = choices)

@colander.deferred
def deferred_default_lang(node, kw):
    request = kw['request']
    return request.GET.get('language', request.locale_name)
