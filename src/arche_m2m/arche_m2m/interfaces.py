from zope.interface import Attribute
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


#Adapters
# class ILanguages(Interface):
#     pass
# 
# 
# class INamedSingleRelation(Interface):
#     name = Attribute("Namespace for this relation. Should be the same as the registered name for this adapter")
#     data = Attribute("Data storage")
#     reverse = Attribute("Reversed data storage")
#     
#     def __init__(context):
#         """ Initialize adater """
#     def get(key, failobj = None): pass
#     def __getitem__(key): pass
#     def __len__(): pass
#     def __contains__(key): pass