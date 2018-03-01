"""
Defines a Django management command class to override django.contrib.auth's createsuperuser.

See:
    https://docs.djangoproject.com/en/dev/ref/django-admin/#createsuperuser

In true Django fashion, the standard, almost every aspect of the simple Python libraries in use have
been wrapped to oblivion and back, creating additional layers of complexity with marginal benefit.
There are two methods by which management commands can be run: from the command line and from code
with django.core.management.call_command(). Both methods call argparse.parse_args(), resulting in


See:
    https://github.com/django/django/blob/master/django/core/management/base.py
    https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py

"""
import django.contrib.auth.management.commands.createsuperuser


class Command(django.contrib.auth.management.commands.createsuperuser.Command):
    """
    A Django management command class that adds an option to specify the new user's password.

    Under the standard createsuperuser management command, the new superuser's password MUST either
    be unset, in which case the user cannot log in, or must be set interactively through an
    interactive terminal session. Similarly, the changepassword command requires an interactive
    session.

    This command allows the setting of the new superuser's password noninteractively.

    See:
        https://docs.djangoproject.com/en/dev/ref/django-admin/#createsuperuser

    """
    def add_arguments(self, parser):
        """
        Override the parent's argument definition, adding a noninteractive password option.

        For future work and readability, I'm going to specify the argparse arguments verbosely.

        See:
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#accepting-optional-arguments
            https://docs.python.org/3/library/argparse.html#the-add-argument-method

        """
        parser.add_argument(
            '-p', '--password',
            action='store',
            nargs='+',
            help=(
                'The value of the new superuser\'s password. '
                'Warning: this is insecure and should be used only during development or '
                'during a deployment such as to allow a temporary first login to the admin site.'
            )
        )
        super().add_arguments(parser)
        # Add random password generation with output to stdout?

    def handle(self, *args, **options):
        super().handle(*args, **options)
        # Check for multiple arguments
        # Need to handle invalid password errors from
        #   https://github.com/django/django/blob/master/django/contrib/auth/base_user.py
