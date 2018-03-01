"""
This module defines tests of the overridden "createsuperuser" management command.

"""
import django.core.management
import django.test


class TestCreateSuperUserOverride(django.test.TestCase):
    """
    A test suite of the createsuperuser override.

    """

    def test_password_argument(self):
        """
        Test that the new password argument is accepted.

        Django's management command framework is built around Python's built-in argparse library.
        argparse.parse_args() is called which will raise

        See:
            https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
            https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args
            https://docs.python.org/3/library/argparse.html#partial-parsing

        """
        import pdb; pdb.set_trace()
