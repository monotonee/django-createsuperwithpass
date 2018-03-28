"""
This module defines tests of the overridden "createsuperuser" management command.

In addition to Django's existing tests of contrib.auth's createsuperuser, the management command
override must pass these tests. Most cases in which the password option is omitted are NOT tested
here as the overridden command should fall back to contrib.auth's behavior in such cases and should
therefore pass all of the relevant, built-in Django tests.

I had originally attempted to run the "createsuperuser" override against Django's built-in test
suite to ensure that the command fell back to the standard command algorithm when no password option
was passed but, due to the way Django's test environment is designed and initialized, this proved
prohibitively time-consuming and, unfortunately, I've largely lost the will to fight Django's dated
design decisions any longer.

See:
    https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
    https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_args
    https://docs.python.org/3/library/argparse.html#partial-parsing
    https://docs.djangoproject.com/en/dev/ref/django-admin/#running-management-commands-from-your-code

"""
import io
import unittest.mock

import django.core.management
import django.test

from . import utils


class TestInteractiveMode(django.test.TestCase):
    """
    A test suite of the createsuperuser management command override in INTERACTIVE mode.

    See:
        https://docs.djangoproject.com/en/dev/ref/django-admin/#createsuperuser
        https://github.com/django/django/blob/master/tests/auth_tests/test_management.py

    """
    def setUp(self):
        """
        Execute tasks once before every test.

        See:
            https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUp

        """
        self.stderr = io.StringIO()
        self.stdout = io.StringIO()

    def tearDown(self):
        """
        Execute tasks once after every test.

        See:
            https://docs.python.org/3/library/unittest.html#unittest.TestCase.tearDown

        """
        self.stderr.close()
        self.stdout.close()

    def test_exception_no_tty(self):
        """
        Ensure that an exception is raised if no I/O available in interactive mode.

        The createsuperuser command defaults to interactive mode but, even if interactive mode is
        explicitly enabled, an exception will be raised if the command's environment does not
        support input and output necessary for interactivity.

        """
        pass

    def test_password_option_omitted_prompt(self):
        """
        When the password option is omitted, test that password prompt is issued.

        When no password option is used in interactive mode, ensure fallback to standard
        contrib.auth behavior in which the user is prompted for a password.

        See:
            https://docs.djangoproject.com/en/dev/ref/django-admin/#createsuperuser

        """
        pass

    def test_password_option_present_no_exception(self):
        """
        Ensure that no exception is raised for an "unknown argument" when password option is passed.

        Under the hood, argparse raises a SystemExit exception when an unknown argument is passed,
        unless parse_known_args() was called instead of parse_args(). Django wraps
        argparse.ArgumentParser but allows the SystemExit exception to be raised when in
        interactive mode.

        See:
            https://github.com/django/django/blob/master/django/core/management/base.py

        """
        pass

    def test_password_option_present_no_prompt(self):
        """
        In interactive env, ensure no password prompted when the password option is present.

        When the password option is passed with a valid argument in an interactive execution, ensure
        that contrib.auth behavior is overridden and user is NOT prompted for a password value.

        """
        pass

    def test_password_option_present_saved(self):
        """
        Test that the password option is saved successfully.

        When the password option is passed with a valid argument in an interactive execution, ensure
        that contrib.auth behavior is overridden and user is NOT prompted for a password value and
        NO exception is raised.

        Django's management command framework is built around Python's built-in argparse library for
        argument parsing. By default, when unknown options are encountered, argparse will raise
        a SystemExit exception. Ensure that the password option is NOT unknown to the
        createsuperuser command and that it will NOT cause a SystemExit exception.

        Note that argparse.ArgumentParser.parse_known_args() will not raise SystemExit on unknown
        options passed but this behavior is not used by the Django management command framework.

        See:
            https://docs.python.org/3/library/exceptions.html#SystemExit
            https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.parse_known_args

        """
        pass

    def test_password_option_present_validation(self):
        """
        Ensure that the password value is validated by all active password validators.

        See:
            https://docs.djangoproject.com/en/dev/topics/auth/passwords/#module-django.contrib.auth.password_validation

        """
        pass

    def test_username_prompt_string(self):
        """
        Test that the correct prompt string is issued for the username value.

        """
        pass


class TestNoninteractiveMode(django.test.TestCase):
    """
    A test suite of the createsuperuser management command override in NONINTERACTIVE mode.

    See:
        https://docs.djangoproject.com/en/dev/ref/django-admin/#createsuperuser
        https://github.com/django/django/blob/master/tests/auth_tests/test_management.py

    """

    def test_password_option_omitted(self):
        """
        Test fallback to standard Django behavior when password option is omitted.

        The standard contrib.auth createsuperuser command should create a new superuser without a
        password set.

        """
        pass

    def test_password_option_present_no_exception(self):
        """
        Ensure that no exception is raised for an "unknown argument" when password option is passed.

        Under the hood, argparse raises a SystemExit exception when an unknown argument is passed,
        unless parse_known_args() was called instead of parse_args(). Django wraps
        argparse.ArgumentParser and raises a CommandException in noninteractive mode.

        See:
            https://github.com/django/django/blob/master/django/core/management/base.py

        """
        pass

    def test_password_option_present_saved(self):
        """
        Test that the password option's value is successfully saved.

        When the password option is passed with a valid argument in a noninteractive execution,
        ensure that the database contains a usable value for the new superuser.

        The standard contrib.auth createsuperuser command has no way to create a new superuser
        with a password in noninteractive mode. Ensure that that behavior is correctly overridden.

        """
        pass

    def test_password_option_present_validation(self):
        """
        Ensure that the password value is validated by all active password validators.

        See:
            https://docs.djangoproject.com/en/dev/topics/auth/passwords/#module-django.contrib.auth.password_validation

        """
        pass
