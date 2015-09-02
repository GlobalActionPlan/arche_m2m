from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('arche_m2m')


def includeme(config):
    config.include('.ttw_translations')
    config.include('.models')
    config.include('.views')
    config.include('.permissions')
    config.add_translation_dirs('arche_m2m:locale')
