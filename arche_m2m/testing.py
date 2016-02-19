
def question_fixture(root):
    from arche_m2m.models.question import Question
    from arche_m2m.models.question_type import Choice
    from arche_m2m.models.question_type import QuestionType
    from arche_m2m.models.question_types import QuestionTypes
    from arche_m2m.models.questions import Questions
    root['questions'] = Questions()
    root['qtypes'] = QuestionTypes()
    root['qtypes']['qt1'] = qt1 = QuestionType(uid = 'qt_uid', input_widget = 'dropdown_choice_widget')
    root['qtypes']['qt2'] = qt2 = QuestionType(uid = 'qt_uid2', input_widget = 'dropdown_choice_widget')
    root['qtypes']['qt3'] = qt3 = QuestionType(uid = 'qt_uid3', input_widget = 'dropdown_choice_widget')
    qt1['c1'] = Choice(cluster = 'a', uid = 'c_uid1', language = 'sv')
    qt1['c2'] = Choice(cluster = 'a', uid = 'c_uid2', language = 'en')
    qt1['c3'] = Choice(cluster = 'b', uid = 'c_uid3', language = 'sv')
    qt2['c1'] = Choice(cluster = 'c', uid = 'c_uid4', language = 'sv')
    qt3['c1'] = Choice(cluster = 'f', uid = 'c_uid7', language = 'sv')
    root['questions']['q1'] = Question(question_type = 'qt_uid', cluster = 'q_cluster', language = 'sv')
    root['questions']['q2'] = q2 = Question(question_type = 'qt_uid2', cluster = 'q_cluster2', language = 'sv')
    root['questions']['q3'] = q3 = Question(question_type = 'qt_uid3', cluster = 'q_cluster3', language = 'sv')
    root['questions']['q4'] = q4 = Question(question_type = 'qt_uid4', cluster = 'q_cluster3', language = 'en')
    q2['c2'] = Choice(cluster = 'd', uid = 'c_uid5', language = 'sv')
    q2['c3'] = Choice(cluster = 'e', uid = 'c_uid6', language = 'sv')
    q3['c2'] = Choice(cluster = 'f', uid = 'c_uid8', language = 'sv')
    q3['c3'] = Choice(cluster = 'g', uid = 'c_uid9', language = 'sv')
    q4['c2'] = Choice(cluster = 'f', uid = 'c_uid10', language = 'en')
    q4['c3'] = Choice(cluster = 'g', uid = 'c_uid11', language = 'en')
