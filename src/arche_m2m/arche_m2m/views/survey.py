from __future__ import unicode_literals

from arche import security
from arche.views.base import BaseForm
from arche.views.base import BaseView
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config
from pyramid.decorator import reify
from pyramid_mailer.message import Message
from pyramid.renderers import render
import colander
import deform
from pyramid_mailer import get_mailer

from arche_m2m import _
from arche_m2m.interfaces import ISurvey
from arche_m2m.interfaces import IQuestionnaire
from arche_m2m.interfaces import IQuestionWidget
from pyramid.traversal import find_interface


class SurveyView(BaseView):
    """ Will redirect to view for managers if user has edit permission,
        otherwise do the survey
    """

    @view_config(context = ISurvey,
                 name = "do",
                 permission = security.NO_PERMISSION_REQUIRED,
                 renderer = "arche_m2m:templates/survey_start.pt")
    def do_survey(self):
        #if self.request.has_permission(security.PERM_EDIT):
        #   url = self.request.resource_url(self.context, 'view')
        #   return HTTPFound(location = url)
        #first section
        next_section = None
        for obj in self.context.values():
            next_section = obj
            break
        uid = self.request.GET.get('uid', '')
        return {'start_link': self.request.resource_url(next_section, query = {'uid': uid})}


@view_config(context = ISurvey, name = "view", permission = security.PERM_EDIT,
             renderer = "arche_m2m:templates/survey_view.pt")
class ManageSurveyView(BaseView):
    """ View for administrators
    """
    def __call__(self):
        return {}


@view_config(name='participants',
             context=ISurvey,
             renderer='arche_m2m:templates/survey_participans.pt',
             permission=security.PERM_EDIT)
class ManageParticipantsView(BaseView):

    def __call__(self):
        """ Overview of participants. """
        response = {}
        response['participants'] = participants = self.context.get_participants_data()
        not_finished = [x for x in participants if x['finished']<100]
        response['not_finished'] = not_finished
        #self.response['closed_survey'] = self._closed_survey(self.context)
        #schema = createSchema(self.context.schemas['reminder'])
        #schema = schema.bind(context = self.context, request = self.request)
        #form = Form(schema, buttons=(self.buttons['send'],))
        #self.response['form_resources'] = form.get_widget_resources()

        #post = self.request.POST
        #if 'send' in post:
        #    controls = self.request.POST.items()
#             try:
#                 appstruct = form.validate(controls)
#             except ValidationFailure, e:
#                 self.response['form'] = e.render()
#                 return self.response
# 
#             for participant in not_finished:
#                 # a participant with less then 100% completion will receive the invite ticket again with specified message
#                 ticket_uid = participant['uid']
#                 email = self.context.tickets[ticket_uid]
#                 self.context.send_invitation_email(self.request, email, ticket_uid, appstruct['subject'], appstruct['message'])
# 
#             self.add_flash_message(_(u"Reminder has been sent"))
# 
#         self.response['form'] = form.render()
        return response


@view_config(context = IQuestionnaire,
             permission = security.NO_PERMISSION_REQUIRED,
             renderer = "arche:templates/form.pt")
class QuestionnaireForm(BaseForm):

    @property
    def survey(self):
        return find_interface(self.context, ISurvey)

    @property
    def participant_uid(self):
        return self.request.params.get('uid', '')

    @property
    def buttons(self):
        #Check if this is first etc
        buttons = []
        if self._previous_section():
            buttons.append(deform.Button(name = 'previous', type = 'button', css_class = 'btn btn-default'))
        #XXX
        buttons.append(deform.Button(name = 'next', css_class = 'btn btn-primary'))
        return buttons

    def __call__(self):
        #FIXME: This is slow and stupid.
        if not self.participant_uid and self.request.has_permission(security.PERM_EDIT):
            return HTTPFound(location = self.request.resource_url(self.context, 'view'))
        if not self.participant_uid in self.survey.tokens.values():
            raise HTTPForbidden("Invalid ticket")
        self.create_schema()
        return super(BaseForm, self).__call__()

    def create_schema(self):
        self.schema = colander.Schema(title = _("Questionnaire"))
        for uid in self.context.question_ids:
            question = self.resolve_uid(uid)
            question_type = self.resolve_uid(question.question_type)
            question_widget = self.request.registry.queryAdapter(question_type,
                                                                 IQuestionWidget,
                                                                 name = getattr(question_type, 'input_widget', ''))
            if question_widget:
                self.schema.add(question_widget.node(question.uid, title = question.title))

    def appstruct(self):
        return self.context.responses.get(self.participant_uid, {})

    def _next_section(self):
        """ Return next section object if there is one.
        """
        parent = self.context.__parent__
        section_order = tuple(parent.order)
        cur_index = section_order.index(self.context.__name__)
        try:
            next_name = section_order[cur_index+1]
            return parent[next_name]
        except IndexError:
            return

    def _previous_section(self):
        """ Return previous section object if there is one.
        """
        parent = self.context.__parent__
        section_order = tuple(parent.order)
        cur_index = section_order.index(self.context.__name__)
        if cur_index == 0:
            #Since -1 is a valid index :)
            return
        try:
            previous_name = section_order[cur_index-1]
            return parent[previous_name]
        except IndexError:
            return  

    def _link(self, obj):
        uid = self.request.GET.get('uid', '')
        return self.request.resource_url(obj, query = {'uid': uid})

    def next_success(self, appstruct):
        #FIXME: Is this an okay way to save data? It should always be marked as dirty
        #but how about nested non-persistent structures within appstruct?
        self.context.responses[self.participant_uid] = appstruct
        next_section = self._next_section()
        #Do stuff if finished
        return HTTPFound(location = self._link(next_section))

    def previous_success(self, appstruct):
        self.context.responses[self.participant_uid] = appstruct
        return self.go_previous()

    def go_previous(self, *args):
        previous = self._previous_section()
        if previous is None:
            previous = self.context.__parent__        
        return HTTPFound(location = self._link(previous))
    previous_failure = go_previous


@view_config(context = IQuestionnaire,
             name = 'view',
             permission = security.NO_PERMISSION_REQUIRED,
             renderer = "arche:templates/form.pt")
class DummyQuestionnaireForm(QuestionnaireForm):

    def __call__(self):
        self.create_schema()
        return super(BaseForm, self).__call__()

    def _link(self, obj):
        return self.request.resource_url(obj, 'view')

    def next_success(self, *args):
        next_section = self._next_section()
        #Do stuff if finished
        return HTTPFound(location = self._link(next_section))

    next_failure = next_success

    def previous_success(self, appstruct):
        return self.go_previous()



@view_config(context = ISurvey,
             name = 'invite',
             permission = security.PERM_EDIT,
             renderer = "arche:templates/form.pt")
class SendInvitationForm(BaseForm):
    schema_name = "send_invitation"
    type_name = "Survey"
    buttons = (deform.Button('send'),)

    @reify
    def mailer(self):
        return get_mailer(self.request)

    def send_success(self, appstruct):
        """ Performed when send button is clicked, and schema validates correctly. """
        #FIXME: It might be smarter to create a schema type that splits rows into a list
        emails = set()
        for email in appstruct['emails'].splitlines():
            emails.add(email.strip())
        appstruct['emails'] = emails
        self.send_invitations(**appstruct)
        self.flash_messages.add(_("Invitations sent"))
        return HTTPFound(location = self.request.resource_url(self.context))

    def send_invitations(self, emails=(), subject=None, message=None):
        """ Send out invitations to any emails stored as invitation_emails.
            Creates a ticket that a survey participant will "claim" to start the survey.
            Also removes emails from invitation pool.
        """
        for email in emails:
            invitation_uid = self.context.create_token(email)
            self.send_invitation_email(email, invitation_uid, subject, message)
        
    def send_invitation_email(self, email, uid, subject, message):
        #sender = self.get_field_value('from_address', '')
        sender = None #FIXME
        response = {}
        response['access_link'] = self.request.resource_url(self.context, 'do', query = {'uid': uid})
        response['message'] = message
        response['subject'] = subject
        body_html = render('arche_m2m:templates/mail/survey_invitation.pt',
                           response, request = self.request)
        #Must contain link etc, so each mail must be unique
        msg = Message(subject = subject,
                      sender = sender and sender or None,
                      recipients = [email.strip()],
                      html = body_html)
        self.mailer.send(msg)

# class BaseForm(BaseView, FormView):
#     default_success = _(u"Done")
#     default_cancel = _(u"Canceled")
#     schema_name = u''
#     type_name = u''
#     heading = u''
# 
#     button_delete = deform.Button('delete', title = _(u"Delete"), css_class = 'btn btn-danger')
#     button_cancel = deform.Button('cancel', title = _(u"Cancel"), css_class = 'btn btn-default')
#     button_save = deform.Button('save', title = _(u"Save"), css_class = 'btn btn-primary')
#     button_add = deform.Button('add', title = _(u"Add"), css_class = 'btn btn-primary')
# 
#     buttons = (button_save, button_cancel,)
# 
#     def __call__(self):
#         #Only change schema if nothing exist already.
#         #Subclasses may have a custom schema constructed
#         if not getattr(self, 'schema', False):
#             schema_factory = self.get_schema_factory(self.type_name, self.schema_name)
#             if not schema_factory:
#                 err = _(u"Schema type '${type_name}' not registered for content type '${schema_name}'.",
#                         mapping = {'type_name': self.type_name, 'schema_name': self.schema_name})
#                 raise HTTPForbidden(err)
#             self.schema = schema_factory()
#         result = super(BaseForm, self).__call__()
#         return result
# 
#     def get_schema_factory(self, type_name, schema_name):
#         try:
#             return get_content_schemas(self.request.registry)[type_name][schema_name]
#         except KeyError:
#             pass
# 
#     def _tab_fields(self, field):
#         results = {}
#         for child in field:
#             tab = getattr(child.schema, 'tab', '')
#             fields = results.setdefault(tab, [])
#             fields.append(child)
#         return results
# 
#     @property
#     def tab_titles(self):
#         #FIXME adjustable
#         from arche.schemas import tabs
#         return tabs
# 
#     @property
#     def form_options(self):
#         return {'action': self.request.url,
#                 'heading': getattr(self, 'heading', ''),
#                 'tab_fields': self._tab_fields,
#                 'tab_titles': self.tab_titles}
# 
#     def get_bind_data(self):
#         return {'context': self.context, 'request': self.request, 'view': self}
# 
#     def appstruct(self):
#         appstruct = {}
#         for field in self.schema.children:
#             if hasattr(self.context, field.name):
#                 val = getattr(self.context, field.name)
#                 if val is None:
#                     val = colander.null
#                 appstruct[field.name] = val
#         return appstruct
# 
#     def cancel(self, *args):
#         self.flash_messages.add(self.default_cancel)
#         return HTTPFound(location = self.request.resource_url(self.context))
#     cancel_success = cancel_failure = cancel