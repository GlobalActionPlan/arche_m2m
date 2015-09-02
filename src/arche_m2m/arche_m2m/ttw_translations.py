from arche_ttw_translation.models import Translatable

ttwt = Translatable()

ttwt['start_btn'] = 'Start'



def includeme(config):
    config.include('arche_ttw_translation')
    config.register_ttwt(ttwt)
