from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('arche_m2m')


def includeme(config):
    config.include('.models')
    config.include('.views')
