from arche_ttw_translation.models import Translatable

ttwt = Translatable()

ttwt['start_btn'] = 'Start'
ttwt['next_btn'] = 'Next'
ttwt['previous_btn'] = 'Previous'
ttwt['done'] = 'Done'
ttwt['participant_done_text'] = 'Thank you for filling out the survey. In case you need to change anything, simply press the button below.'
ttwt['participate_btn'] = 'Participate in the survey'
ttwt['email_sent'] = 'Email sent successfully'
ttwt['link_to_start_survey'] = 'Link to start survey'

def includeme(config):
    config.include('arche_ttw_translation')
    config.register_ttwt(ttwt)
