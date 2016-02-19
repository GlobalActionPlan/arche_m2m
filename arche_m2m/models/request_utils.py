from arche_m2m.interfaces import IQuestion
from arche_m2m.interfaces import IQuestionType
from arche_m2m.interfaces import IQuestionWidget
from arche_m2m.interfaces import ISurveySection


def get_question_widget(request, context):
    """
    :param context: Question or QuestionType instance.
    :return: QuestionWidget instance specified by the QuestionType.
    """
    if IQuestion.providedBy(context):
        context = get_question_type(request, context)
    if not IQuestionType.providedBy(context):
        raise TypeError("context must be a Question or QuestionType object") #pragma: no coverage
    return request.registry.queryAdapter(context, IQuestionWidget, name = context.input_widget)

def get_question_type(request, context):
    """
    :param context: Question instance.
    :return: corresponding QuestionType instance.
    """
    if not IQuestion.providedBy(context):
        raise TypeError("context must be a Question object") #pragma: no coverage
    if not context.question_type:
        raise ValueError("%r doesn't have the question_type attribute set" % context) #pragma: no coverage
    for docid in request.root.catalog.query("uid == '%s'" % context.question_type)[1]:
        for obj in request.resolve_docids(docid, perm = None):
            #Generator with one item in this case
            return obj
    raise ValueError("%r has a question_type set that doesn't exist" % context)

def get_picked_choice(request, section, question, participant_uid, default = None, lang = None):
    """
    Only works on questions with single choice questions right now.

    :param section: SurveySection instance
    :param question: Question instance
    :param participant_uid: Respondent (survey participant) id.
    :param default: Return this if not found.
    :return: Choice object or default.
    """
    if not ISurveySection.providedBy(section):
        raise TypeError("section must be a SurveySection object") #pragma: no coverage
    if not IQuestion.providedBy(question):
        raise TypeError("question must be a Question object") #pragma: no coverage
    if lang is None:
        lang = request.locale_name
    question_widget = get_question_widget(request, question)
    if question_widget.allow_choices == True and question_widget.multichoice == False:
        choice_id = section.responses.get(participant_uid, {}).get(question.cluster)
        if choice_id:
            query = "type_name == 'Choice' and cluster == '%s'" % choice_id
            for docid in request.root.catalog.query(query + " and language == '%s'" % lang)[1]:
                #Generator with one item in this case
                for obj in request.resolve_docids(docid, perm = None):
                    return obj
            for docid in request.root.catalog.query(query)[1]:
                #Generator that may have more items, but we're interested in any of them
                for obj in request.resolve_docids(docid, perm = None):
                    return obj
    return default

def includeme(config):
    config.add_request_method(get_question_widget)
    config.add_request_method(get_question_type)
    config.add_request_method(get_picked_choice)
