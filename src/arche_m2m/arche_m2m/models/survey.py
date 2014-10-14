from __future__ import unicode_literals
from decimal import Decimal

from BTrees.OOBTree import OOBTree
from arche.api import Content
from arche.api import LocalRolesMixin
from arche.api import Token
from zope.interface import implementer
import colander
import deform

from arche_m2m import _
from arche_m2m.interfaces import ISurveySection
from arche_m2m.interfaces import ISurvey
from arche_m2m.models.i18n import TranslationMixin
from arche_m2m.models.i18n import deferred_translations_node
from arche_m2m.schemas.validators import multiple_email_validator


@implementer(ISurvey)
class Survey(Content, LocalRolesMixin, TranslationMixin):
    type_title = _("Survey")
    type_name = "Survey"
    add_permission = "Add %s" % type_name

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


class SurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                translate = True,
                                translate_missing = "",
                                title = _("Title"))
    translations = deferred_translations_node


class SurveyInvitationSchema(colander.Schema):
    subject = colander.SchemaNode(colander.String(),
                                  title = _(u"Email subject and text header"),
                                  description = _(u"Will be visible in the subject line, and as a header in the email body."))
    message = colander.SchemaNode(colander.String(),
                                  title = _(u"Message - please note that the link will be added as a new line below the message!"),
                                  widget = deform.widget.RichTextWidget(),
                                  default = _(u'Please fill in the survey. Click the link below to access it:'),)
    emails = colander.SchemaNode(colander.String(),
                                 title = _(u"Participant email addresses - add one per row."),
                                 description = _(u"invitation_emails_lang_notice",
                                                 default = u"Remember to only add users who should recieve the message in this language."),
                                 validator = multiple_email_validator,
                                 widget=deform.widget.TextAreaWidget(rows=10, cols=50),)


def includeme(config):
    config.add_content_factory(Survey)
    config.add_addable_content("Survey", ("Root", "Document", "Organisation"))
    config.add_content_schema('Survey', SurveySchema, 'edit')
    config.add_content_schema('Survey', SurveySchema, 'add')
    config.add_content_schema('Survey', SurveyInvitationSchema, 'send_invitation')
