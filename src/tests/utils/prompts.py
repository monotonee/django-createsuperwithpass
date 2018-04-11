import functools

import django.contrib.auth


def _find_prompt_keyword(keyword, prompt):
    substr_index = prompt.lower().find(keyword.lower())
    return substr_index >= 0


def _get_username_field_name():
    user_model = django.contrib.auth.get_user_model()
    username_field = user_model._meta.get_field(user_model.USERNAME_FIELD)
    return username_field.verbose_name


# In the standard contrib.auth user model, the email field is part of User.REQUIRED_FIELDS, a
# constant containing fields that require input from such commands as createsuperuser. It is
# therefore possible to define tests and the respective prompt keywords dynamically based on the
# fields present in REQUIRED_FIELDS. However, I don't consider a dynamic constant definition worth
# the time since I know that this package's tests will be using the default contrib.auth user model
# and that, even if new REQUIRED_FIELDS are added, it is quite posible that they will contain custom
# validators just like the email field, meaning that any "universal" value for all fields may fail
# and cause an exception to be raised. Therefore, despite an effort to insulate this module through
# dynamic keyword definition, any changes to the user model are just as likely to break this
# utility.
_KEYWORD_EMAIL = 'email'
_KEYWORD_PASSWORD = 'password'
_KEYWORD_USERNAME = _get_username_field_name()


EMAIL = functools.partial(_find_prompt_keyword, _KEYWORD_EMAIL)
PASSWORD = functools.partial(_find_prompt_keyword, _KEYWORD_PASSWORD)
USERNAME = functools.partial(_find_prompt_keyword, _KEYWORD_USERNAME)
