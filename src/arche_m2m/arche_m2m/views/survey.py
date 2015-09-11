from __future__ import unicode_literals
from decimal import Decimal

from arche import security
from arche.views.base import BaseForm
from arche.views.base import BaseView
from BTrees._OOBTree import OOBTree
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.traversal import find_interface
from pyramid.view import view_config
from pyramid_mailer import get_mailer
import colander
import deform

from arche.models.workflow import get_context_wf
from arche_m2m import _
from arche_m2m.fanstatic import manage_css
from arche_m2m.fanstatic import survey_manage
from arche_m2m.interfaces import IOrganisation
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import ISurvey
from arche_m2m.interfaces import ISurveySection
from arche_m2m.permissions import PARTICIPATE_SURVEY
from arche_m2m.interfaces import ILangCodes


def calc_percentages(section):
    survey = find_interface(section, ISurvey)
    total = 0
    before = 0
    current = 0
    is_before = True
    for obj in survey.values():
        this_count = len(getattr(obj, 'question_ids', ()))
        total += this_count
        if obj == section:
            is_before = False
            current = this_count
            continue
        if is_before:
            before += this_count
    before_perc = 0
    current_perc = 0
    if before:
        before_perc = int(round(Decimal(before)/Decimal(total) * 100))
    if current:
        current_perc = int(round(Decimal(current)/Decimal(total) * 100))
    return before_perc, current_perc


@view_config(context = ISurvey,
             name = "add_yourself",
             permission = security.NO_PERMISSION_REQUIRED,
             renderer = "arche_m2m:templates/form_participant.pt")
class SelfInviteForm(BaseForm):
    schema_name = 'add_yourself'
    type_name = 'Survey'

    def __call__(self):
        wf = get_context_wf(self.context)
        if self.context.allow_anonymous_to_invite_themselves == True and wf.state == 'open':
            return super(SelfInviteForm, self).__call__()
        raise HTTPForbidden()

    def save_success(self, appstruct):
        email = appstruct['email']
        invitation_uid = str(self.context.create_token(email))
        subject = self.request.ttwt('link_to_start_survey', 'Link to start survey')
        _send_invitation_email(self, email, invitation_uid, subject)
        msg = self.request.ttwt('email_sent', 'Email sent successfully')
        self.flash_messages.add(msg, type = 'success', auto_destruct = False)
        return HTTPFound(location = self.request.resource_url(self.context, 'do'))


class SurveyView(BaseView):
    """ Will redirect to view for managers if user has edit permission,
        otherwise do the survey
    """

    @view_config(context = ISurvey,
                 name = "do",
                 permission = security.NO_PERMISSION_REQUIRED,
                 renderer = "arche_m2m:templates/survey_start.pt")
    def do_survey(self):
        if not self.request.has_permission(PARTICIPATE_SURVEY):
            return HTTPFound(location = self.request.resource_url(self.context, 'closed'))
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
        lang_codes = self.request.registry.getUtility(ILangCodes)
        return {'uid': uid, 'next_section': next_section, 'lang_codes': lang_codes}

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

    @view_config(context = ISurvey,
                 name = "closed",
                 permission = security.NO_PERMISSION_REQUIRED,
                 renderer = "arche_m2m:templates/survey_closed.pt")
    def survey_closed(self):
        return {}


class ManageSurveyView(BaseView):
    """ View for administrators
    """

    @reify
    def organisation(self):
        return find_interface(self.context, IOrganisation)

    @view_config(context = ISurvey, name = "view",
                 permission = security.NO_PERMISSION_REQUIRED,
                 renderer = "arche_m2m:templates/survey_view.pt")
    def view(self):
        #Is the current user a manager?
        if self.request.has_permission(security.PERM_VIEW, self.context):
            return {}
        #This is not a manager - in some cases users are allowed to start the survey anyway
        return HTTPFound(location = self.request.resource_url(self.context, 'do'))

    def process_question_ids(self):
        sect_id_questions = self.request.POST.dict_of_lists()
        for section in self.context.values():
            if ISurveySection.providedBy(section):
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
        response = {}
        picked_questions = set()
        survey_sections = []
        for section in self.context.values():
            if not ISurveySection.providedBy(section):
                continue
            picked_questions.update(section.question_ids)
            survey_sections.append(section)
        response['survey_sections'] = survey_sections
        if not survey_sections:
            msg = _(u"no_sections_added_notice",
                    default = u"You need to add a Survey section "
                        "and then use this view to manage the questions.")
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


@view_config(context = ISurveySection,
             permission = security.NO_PERMISSION_REQUIRED,
             renderer = "arche_m2m:templates/survey_form_participant.pt")
class SurveySectionForm(BaseForm):

    @property
    def buttons(self):
        return (deform.Button(name = 'previous',
                              title = self.request.ttwt('previous_btn', 'Previous'),
                              css_class = 'btn btn-default'),
                deform.Button(name = 'next',
                              title = self.request.ttwt('next_btn', 'Next'),
                              css_class = 'btn btn-primary submit-default'))

    @reify
    def survey(self):
        return find_interface(self.context, ISurvey)

    @property
    def participant_uid(self):
        return self.request.params.get('uid', '')

    @reify
    def organisation(self):
        return find_interface(self.context, IOrganisation)

    def __call__(self):
        #FIXME: This is slow and stupid.
        if not self.participant_uid and self.request.has_permission(security.PERM_VIEW):
            return HTTPFound(location = self.request.resource_url(self.context, 'view'))
        if not self.participant_uid in self.survey.tokens.values():
            raise HTTPForbidden("Invalid ticket")
        return super(BaseForm, self).__call__()

    def get_schema(self):
        locale_name = self.request.locale_name
        title = self.context.translate('title', locale_name)
        description = self.context.translate('body', locale_name)
        schema = colander.Schema(title = title, description = description)
        for qid in self.context.question_ids:
            docids = self.catalog_search(cluster = qid, language = self.request.locale_name)
            if docids:
                question = None
                for question in self.resolve_docids(docids, perm = None):
                    #Only one or none
                    pass
                question_type = self.resolve_uid(question.question_type, perm = None)
                question_widget = self.request.registry.queryAdapter(question_type,
                                                                     IQuestionWidget,
                                                                     name = getattr(question_type, 'input_widget', ''))
                if question_widget:
                    title = question.title
                    if self.organisation:
                        title = self.organisation.variants.get(question.uid, title)
                    schema.add(question_widget.node(question.cluster,
                                                         lang = self.request.locale_name,
                                                         question = question,
                                                         title = title))
            else:
                schema.add(colander.SchemaNode(colander.String(),
                                                    widget = deform.widget.TextInputWidget(readonly = True),
                                                    title = _("<Missing question>"),))
        return schema

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
        return HTTPFound(location = self._link(previous))

    previous_failure = go_previous

    def calc_percentages(self):
        return calc_percentages(self.context)


@view_config(context = ISurveySection,
             name = 'view',
             permission = security.PERM_VIEW,
             renderer = "arche:templates/form.pt")
class DummySurveySectionForm(SurveySectionForm):

    def __call__(self):
        return super(BaseForm, self).__call__()

    def _link(self, obj, *args):
        return self.request.resource_url(obj, 'view')

    """ Modify function """
    def next_success(self, *args):
        """
            I recup answers of the param args and after, It's not finish but I will want
             to create a dictionary with the question_id returned by the function : self.context.get_question_id(lang='en')
             in order to match with the correct answer. And I update self.context.responses with it.
        :param args:
        :return:
        """
        # args is a tuple with id and answers of the question in the surveySection


        quest=[]
        quest=self.context.get_question_id(lang='en')

        next_section = self._next_section()
        #Do stuff if finished
        """Modify Not Sure"""
        # I recup answers of questions in the variable args
        val = str(args[0])
        val = val.replace('{','')
        val = val.replace('}','')
        val = val.replace(' ','')
        listo = val.split(',')
        i=0
        for value in listo:
            value=value.split(':')
            value[1] = str(value[1])
            value[1] = value[1].replace('u','',1)
            self.context.responses.update(OOBTree({value[0]:value[1]}))
        """ ******************** """
        if not next_section:
            return HTTPFound(location = self._link(self.context.__parent__, 'done'))
        return HTTPFound(location = self._link(next_section))

    next_failure = next_success

    def previous_success(self, appstruct):
        previous = self._previous_section()
        if previous is None:
            return HTTPFound(location = self._link(self.context.__parent__))
        return HTTPFound(location = self._link(previous))


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
            _send_invitation_email(self, email, invitation_uid, subject, message)
    

def _send_invitation_email(view, email, uid, subject, message = ''):
    response = {}
    response['access_link'] = view.request.resource_url(view.context, 'do', query = {'uid': uid})
    response['message'] = message
    response['subject'] = subject
    body_html = render('arche_m2m:templates/mail/survey_invitation.pt',
                       response, request = view.request)
    view.request.send_email(subject, [email], body_html)
