from __future__ import unicode_literals

from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from pyramid.traversal import resource_path
import colander
import deform

from arche.utils import generate_slug
from arche_m2m import _
from arche_m2m.models.i18n import deferred_translations_node
from arche_m2m.schemas.validators import multiple_email_validator


class SurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                translate = True,
                                translate_missing = "",
                                title = _("Title"))
    translations = deferred_translations_node
    allow_anonymous_to_invite_themselves = colander.SchemaNode(colander.Bool(),
        title = _(u"allow_anonymous_to_invite_themselves_title",
                  default = u"Allow anonymous people to invite themselves to the survey?"),
        description = _(u"allow_anonymous_to_participate_description",
                        default = u"When someone reaches the survey link, allow them to enter "
                            u"their email address to get an invitation and participate in the survey."),
        missing = False,
    )
#    allow_anonymous_to_start = colander.SchemaNode(colander.Bool(),
#        title = _(u"allow_anonymous_to_start_title",
#                  default = u"Allow anonymous people to start the survey without validating their email."),
#        description = _(u"allow_anonymous_to_start_description",
#                        default = u"Last resort - only allow this if there's major email problems with outgoing email!"),
#        missing = False,
#    )


class SurveyInvitationSchema(colander.Schema):
    subject = colander.SchemaNode(colander.String(),
                                  title = _(u"Email subject and text header"),
                                  description = _(u"Will be visible in the subject line, and as a header in the email body."))
    message = colander.SchemaNode(colander.String(),
                                  title = _("survey_invitation_message_title",
                                            default = u"Message - please note that the link will be added as a new line below the message"),
                                  widget = deform.widget.RichTextWidget(),
                                  default = _(u'Please fill in the survey. Click the link below to access it:'),)
    emails = colander.SchemaNode(colander.String(),
                                 title = _(u"Participant email addresses - add one per row."),
                                 description = _(u"invitation_emails_lang_notice",
                                                 default = u"Remember to only add users who should recieve the message in this language."),
                                 validator = multiple_email_validator,
                                 widget=deform.widget.TextAreaWidget(rows=10, cols=50),)

class SurveyAddYourselfSchema(colander.Schema):
    email = colander.SchemaNode(colander.String(),
                                title = _("Your email adress"),
                                description = _("self_invite_form_description",
                                                default = "You'll get an email with the link to start the survey."),
                                validator = colander.Email())


@colander.deferred
def new_parent_widget(node, kw):
    choices = [('', _("<Pick>")), ('/', _("Root"))]
    view = kw['view']
    for obj in view.catalog_query("type_name == 'Survey'", resolve = True):
        choices.append((resource_path(obj), obj.title))
    return deform.widget.SelectWidget(values = choices)

@colander.deferred
def new_name_validator(node, kw):
    context = kw['context']
    return CloneSurveyValidator(context)


class CloneSurveyValidator(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, form, value):
        root = find_root(self.context)
        parent = find_resource(root, value['new_parent'])
        slug = generate_slug(parent, value['new_name'])
        if slug != value['new_name']:
            exc = colander.Invalid(form, _("Check name"))
            exc['new_name'] = _("bad_name_error",
                                default = "Name isn't valid. This would work: '${name}'",
                                mapping = {'name': slug})
            raise exc


class CloneSurveySchema(colander.Schema):
    new_parent = colander.SchemaNode(colander.String(),
                                     title = _("Where do you want to create the new survey?"),
                                     widget = new_parent_widget)
    new_name = colander.SchemaNode(colander.String(),
                                   title = _("New name"),
                                   description = _("Part of the url so use only a-z0-9"),)
    validator = new_name_validator

def includeme(config):
    config.add_content_schema('Survey', SurveySchema, ('edit','add'))
    config.add_content_schema('Survey', SurveyInvitationSchema, 'send_invitation')
    config.add_content_schema('Survey', SurveyAddYourselfSchema, 'add_yourself')
    config.add_content_schema('Survey', CloneSurveySchema, 'clone')
