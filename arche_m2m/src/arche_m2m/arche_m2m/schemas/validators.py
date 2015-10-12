import colander
#from pyramid.traversal import find_root

from arche_m2m import _


def multiple_email_validator(node, value):
    """ Checks that each line of value is a correct email
    """
    validator = colander.Email()
    invalid = []
    for email in value.splitlines():
        email = email.strip()
        if not email:
            continue
        try:
            validator(node, email)
        except colander.Invalid:
            invalid.append(email)
    if invalid:
        emails = ", ".join(invalid)
        raise colander.Invalid(node, _(u"The following addresses is invalid: ${emails}", mapping={'emails': emails}))


# @colander.deferred
# def deferred_confirm_delete_with_title_validator(node, kw):
#     context = kw['context']
#     return ConfirmDeleteWithTitleValidator(context)
# 
# 
# class ConfirmDeleteWithTitleValidator(object):
# 
#     def __init__(self, context, msg = None):
#         self.context = context
#         self.msg = msg and msg or _(u"Doesn't match")
#     
#     def __call__(self, node, value):
#         if self.context.title != value:
#             raise colander.Invalid(node, self.msg)
