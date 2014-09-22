from zope.interface import Interface


class IQuestion(Interface):
    #Should be inherited from some contentish type
    pass

class IQuestionType(Interface):
    pass


class IQuestionWidget(Interface):
    pass

class IChoice(Interface):
    pass


class ISurvey(Interface):
    pass

class IQuestionnaire(Interface):
    pass
