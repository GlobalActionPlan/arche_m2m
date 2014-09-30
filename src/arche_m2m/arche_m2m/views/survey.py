from __future__ import unicode_literals

from arche import security
from arche.views.base import BaseForm
from arche.views.base import BaseView
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.traversal import find_interface
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
import colander
import deform

from arche_m2m import _
from arche_m2m.fanstatic import manage_css
from arche_m2m.fanstatic import survey_manage
from arche_m2m.interfaces import IOrganisation
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import IQuestionnaire
from arche_m2m.interfaces import ISurvey


class SurveyView(BaseView):
    """ Will redirect to view for managers if user has edit permission,
        otherwise do the survey
    """

    @view_config(context = ISurvey,
                 name = "do",
                 permission = security.NO_PERMISSION_REQUIRED,
                 renderer = "arche_m2m:templates/survey_start.pt")
    def do_survey(self):
        if len(self.context.languages) == 1 and self.request.locale_name not in self.context.languages:
            #Select only available language choice before proceeding
            self.request.response.set_cookie('_LOCALE_', value = self.context.languages[0])
            return HTTPFound(location = self.request.url, headers = self.request.response.headers)
        #first section
        next_section = None
        for obj in self.context.values():
            next_section = obj
            break
        uid = self.request.GET.get('uid', '')
        return {'start_link': self.request.resource_url(next_section, query = {'uid': uid})}

    @view_config(context = ISurvey,
                 name = "done",
                 permission = security.NO_PERMISSION_REQUIRED,
                 renderer = "arche_m2m:templates/survey_done.pt")
    def survey_done(self):
        previous_section = None
        for obj in reversed(self.context.values()):
            previous_section = obj
            break
        uid = self.request.GET.get('uid', '')
        return {'previous_link': self.request.resource_url(previous_section, query = {'uid': uid})}    


class ManageSurveyView(BaseView):
    """ View for administrators
    """

    @reify
    def organisation(self):
        return find_interface(self.context, IOrganisation)

    @view_config(context = ISurvey, name = "view", permission = security.PERM_EDIT,
                 renderer = "arche_m2m:templates/survey_view.pt")
    def view(self):
        return {}

    def process_question_ids(self):
        sect_id_questions = self.request.POST.dict_of_lists()
        for section in self.context.values():
            if IQuestionnaire.providedBy(section):
                sect_id_questions.setdefault(section.__name__, [])
        for (sect_id, question_ids) in sect_id_questions.items():
            if sect_id in self.context: #Might be other things than section ids within the post
                self.context[sect_id].question_ids = question_ids

    @view_config(context = ISurvey,
                 name = "manage",
                 permission = security.PERM_EDIT,
                 renderer = "arche_m2m:templates/survey_manage.pt")
    def manage(self):
        survey_manage.need()
        manage_css.need()
        post = self.request.POST
        if 'cancel' in self.request.POST:
            self.flash_messages.add(_("Canceled"))
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)
        if 'save' in post:
            self.process_question_ids()
            self.flash_messages.add(_("Saved"))
            url = self.request.resource_url(self.context, 'manage')
            return HTTPFound(location = url)

        #self.response['organisation'] = org = find_interface(self.context, IOrganisation)
        response = {}
        picked_questions = set()
        survey_sections = []
        for section in self.context.values():
            if not IQuestionnaire.providedBy(section):
                continue
            picked_questions.update(section.question_ids)
            survey_sections.append(section)
        response['survey_sections'] = survey_sections
        if not survey_sections:
            msg = _(u"no_sections_added_notice",
                    default = u"You need to add survey sections and then use this view to manage the questions.")
            self.flash_messages.add(msg, auto_destruct = False)
        #Load all question objects that haven't been picked
        response['available_questions'] = self.get_questions(exclude = picked_questions)
        return response

    def get_questions(self, exclude = ()):
        #Should be optimized
        for obj in self.catalog_search(resolve = True, type_name = 'Question', language = self.request.locale_name):
            if obj.cluster not in exclude:
                yield obj


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
        return response


@view_config(context = IQuestionnaire,
             permission = security.NO_PERMISSION_REQUIRED,
             renderer = "arche_m2m:templates/survey_form_participant.pt")
class QuestionnaireForm(BaseForm):

    @reify
    def survey(self):
        return find_interface(self.context, ISurvey)

    @property
    def participant_uid(self):
        return self.request.params.get('uid', '')

    @property
    def buttons(self):
        #Check if this is first etc
        buttons = []
        buttons.append(deform.Button(name = 'previous', css_class = 'btn btn-default'))
        #XXX
        buttons.append(deform.Button(name = 'next', css_class = 'btn btn-primary submit-default'))
        return buttons

    @reify
    def organisation(self):
        return find_interface(self.context, IOrganisation)

    def __call__(self):
        #FIXME: This is slow and stupid.
        if not self.participant_uid and self.request.has_permission(security.PERM_EDIT):
            return HTTPFound(location = self.request.resource_url(self.context, 'view'))
        if not self.participant_uid in self.survey.tokens.values():
            raise HTTPForbidden("Invalid ticket")
        self.create_schema()
        return super(BaseForm, self).__call__()

    def create_schema(self):
        self.schema = colander.Schema(title = self.context.title)
        for qid in self.context.question_ids:
            docids = self.catalog_search(cluster = qid, language = self.request.locale_name)
            if docids:
                for question in self.resolve_docids(docids):
                    pass
                question_type = self.resolve_uid(question.question_type)
                question_widget = self.request.registry.queryAdapter(question_type,
                                                                     IQuestionWidget,
                                                                     name = getattr(question_type, 'input_widget', ''))
                if question_widget:
                    title = question.title
                    if self.organisation:
                        title = self.organisation.variants.get(question.uid, title)
                    self.schema.add(question_widget.node(question.cluster,
                                                         lang = self.request.locale_name,
                                                         title = title))
            else:
                self.schema.add(colander.SchemaNode(colander.String(),
                                                    widget = deform.widget.TextInputWidget(readonly = True),
                                                    title = _("<Missing question>"),))

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

    def _link(self, obj, *args):
        uid = self.request.GET.get('uid', '')
        return self.request.resource_url(obj, *args, query = {'uid': uid})

    def next_success(self, appstruct):
        #FIXME: Is this an okay way to save data? It should always be marked as dirty
        #but how about nested non-persistent structures within appstruct?
        self.context.responses[self.participant_uid] = appstruct
        next_section = self._next_section()
        #Do stuff if finished
        if not next_section:
            return HTTPFound(location = self._link(self.context.__parent__, 'done'))
        return HTTPFound(location = self._link(next_section))

    def previous_success(self, appstruct):
        self.context.responses[self.participant_uid] = appstruct
        return self.go_previous()

    def go_previous(self, *args):
        previous = self._previous_section()
        if previous is None:
            return HTTPFound(location = self._link(self.context.__parent__, 'do'))
        else:
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

    def _link(self, obj, *args):
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
    title = _("Send invitation(s)")

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
            invitation_uid = str(self.context.create_token(email))
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
