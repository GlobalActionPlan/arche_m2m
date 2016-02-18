from __future__ import unicode_literals
from decimal import Decimal

from BTrees.OOBTree import OOBTree
from arche.api import Content
from arche.api import ContextACLMixin
from arche.api import LocalRolesMixin
from arche.api import Token
from zope.interface import implementer

from arche_m2m import _
from arche_m2m.interfaces import ISurveySection
from arche_m2m.interfaces import ISurvey
from arche_m2m.models.i18n import TranslationMixin
from arche_m2m.permissions import ADD_SURVEY


@implementer(ISurvey)
class Survey(Content, ContextACLMixin, LocalRolesMixin, TranslationMixin):
    type_title = _("Survey")
    type_name = "Survey"
    add_permission = ADD_SURVEY
    allow_anonymous_to_invite_themselves = False
#    allow_anonymous_to_start = False

    def __init__(self, **kw):
        self.tokens = OOBTree()
        super(Survey, self).__init__(**kw)

    def create_token(self, email, size = 15, hours = 0, overwrite = False):
        """ Create a survey invitation token."""
        if email not in self.tokens or (email in self.tokens and overwrite == True):
            token = None
            while token is None or token in self.tokens.values():
                token = Token(size = size, hours = hours)
            self.tokens[email] = token
        return self.tokens[email]

    def get_participants_data(self):
        """Returns the participants with statistics on the survey
        """
        participants = []
        for (email, uid) in self.tokens.items():
            participant = {} 
            participant['uid'] = uid
            participant['email'] = email
            response = 0
            questions = 0
            sections = [x for x in self.values() if ISurveySection.providedBy(x)]
            for section in sections:
                response += len(section.responses.get(uid, {}))
                questions += len(section.question_ids)
            if response != 0:
                participant['finished'] = Decimal(response) / Decimal(questions) * 100
            else:
                participant['finished'] = 0                
            participants.append(participant)
        return participants


def includeme(config):
    config.add_content_factory(Survey, addable_to = ('Root', 'Document', 'Organisation'))
