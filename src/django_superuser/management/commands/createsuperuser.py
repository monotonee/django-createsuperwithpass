"""
Defines a Django management command class to override django.contrib.auth's createsuperuser.

A "password" option is added, allowing non-interactive setting of user passwords. In certain cases,
frameworks shouldn't be so opinionated and shouldn't try so hard to save the users from
themselves like contrib.auth's interactive-only password policy attempts to do. If I wanted to be
babysat like that, I'd be working with Microsoft products.

See:
    https://docs.djangoproject.com/en/dev/ref/django-admin/#createsuperuser
    https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py

Basic overview of management command execution for future reference:

There are two methods by which management commands can be run: from the command line and
programmatically. Execution from the CLI is handled by
django.core.management.execute_from_command_line() while programmatic execution is run through
django.core.management.call_command(). Both methods eventually call argparse.parse_args() instead of
argparse.parse_known_args(), resulting in argparse raising an exception for validation failues such
as the presence of unknown arguments.

The exception raised by argparse in such validation failures is SystemExit. While this is possibly
acceptable for CLI invocations of an argparse-enabled program, programmatic invocations should have
the opportunity to catch raised exceptions. Django, therefore, uses its own
django.core.management.base.CommandParser class, inherited from argparse.ArgumentParser, in which
django.core.management.base.CommandError is instead raised for argument parsing failures in
programmatic executions.

See:
    https://docs.python.org/3/library/exceptions.html#SystemExit
    https://github.com/django/django/blob/master/django/core/management/base.py
    https://github.com/django/django/blob/master/tests/user_commands/tests.py

"""
import django.contrib.auth.management
import django.contrib.auth.management.commands.createsuperuser


class Command(django.contrib.auth.management.commands.createsuperuser.Command):
    """
    A Django management command class that adds an option to specify the new user's password.

    Under the standard contrib.auth's createsuperuser management command, the new superuser's
    password MUST either be unset, in which case the user cannot log in, or must be set
    INTERACTIVELY through an interactive terminal session. Similarly, contrib.auth's changepassword
    command REQUIRES an interactive session. There is no way to non-interactively set a new
    superuser's password or to allow login without a password.

    This command allows the setting of the new superuser's password via a command-line argument
    either interactively or noninteractively.

    See:
        https://docs.djangoproject.com/en/dev/ref/django-admin/#createsuperuser

    """
    def _get_interactive_mode(self, **options):
        """
        Determine if this command is running in interactive mode.

        Interactive mode primarily determined by the --noinput flag, the value of which is saved in
        the "interactive" variable. The value defaults to True but, if --noinput is
        present, the value of "interactive" will be set to False. The parent contrib.auth command
        will ignore the calling environment with regards to determining whether to run interactively
        or noninteractively and will only check for I/O capability if "interactive" is True.

        The "interactive" option is added in contrib.auth's cretesuperuser Command class. It is a
        flag with the argparse action "store_false". However, "interactive" can be forced to contain
        a True value by passing a kwarg through django.core.management.call_command() as it bypasses
        the argparse argument parsing.

        See:
            https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
            https://docs.python.org/3/library/argparse.html#action

        TTY test code was copied directly from contrib.auth's createsuperuser Command.handle().
        self.stdin is defined in the parent's Command.execute() method.

        Args:
            options (dict): The same dictionary of options passed to the command invocation.
                Identical to the options paramater declared by self.handle().

        Returns:
            bool: True if command is running in an interactive context, False otherwise.

        Raises:
            django.contrib.auth.management.commands.createsuperuser.NotRunningInTTYException: If
                the command is instructed to run interactively but the environment doesn't support
                the necessary I/O capabilities.

        See:
            django.contrib.auth.management.commands.createsuperuser.Command.add_arguments()
            https://docs.python.org/3/library/sys.html#sys.stdin
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#django.core.management.BaseCommand.handle

        """
        interactive_option = options.get('interactive', False)
        interactive_tty_session = (hasattr(self.stdin, 'isatty') and self.stdin.isatty())

        if interactive_option and not interactive_tty_session:
            raise django.contrib.auth.management.commands.createsuperuser.NotRunningInTTYException(
                'Not running in a TTY.'
            )

        return interactive_option

    def _get_username_prompt_text(self):
        """
        Generate the string for the username prompt issued in interactive mode.

        Many parts copied from contrib.auth's createsuperuser Command.handle() method.

        Default username is ultimately generated by the Python standard library getpass.getuser().
        See docs page for details.

        Returns:
            str: The specialized username prompt string to be displayed to user in interactive mode
                if the username option was not passed to the command on initial call.

        See:
            https://github.com/django/django/blob/master/django/contrib/auth/management/__init__.py
            https://docs.python.org/3/library/getpass.html

        """
        prompt_string = self.username_field.verbose_name.capitalize()

        # Will return empty string on failure to determine default username.
        default_username = django.contrib.auth.management.get_default_username()
        if default_username:
            prompt_string += " (leave blank to use '{!s}')".format(default_username)

        if self.username_field.remote_field:
            prompt_string += ' {!s}.{!s}'.format(
                self.username_field.remote_field.model._meta.object_name,
                self.username_field.remote_field.field_name
            )

        prompt_string += ':'

        return prompt_string

    def _handle_interactive(self, **options):
        """
        Handle the overridden command logic under INTERACTIVE conditions.

        Args:
            options (dict): The same dictionary of options passed to the command invocation.
                Identical to the options paramater declared by self.handle().

        Returns:
            str: The output, if any, of the command. In the case of this command, most output is
                written directly to stdout.

        See:
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#django.core.management.BaseCommand.handle

        """
        pass

    def _handle_noninteractive(self, **options):
        """
        Handle the overridden command logic under NONINTERACTIVE conditions.

        Args:
            options (dict): The same dictionary of options passed to the command invocation.
                Identical to the options paramater declared by self.handle().

        Returns:
            str: The output, if any, of the command. In the case of this command, most output is
                written directly to stdout.

        See:
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#django.core.management.BaseCommand.handle

        """
        pass

    def add_arguments(self, parser):
        """
        Override the parent's argument definition, adding a password option.

        For future work and readability, I'm going to specify the argparse arguments verbosely.

        See:
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#accepting-optional-arguments
            https://docs.python.org/3/library/argparse.html#the-add-argument-method

        """
        parser.add_argument(
            '-p', '--password',
            action='store',
            dest='password',
            nargs='?',
            help=(
                'The value of the new superuser\'s password. '
                'Warning: this is insecure and should be used only during development or '
                'during a deployment such as to allow a temporary first login to the admin site.'
            )
        )
        super().add_arguments(parser)

    def handle(self, *args, **options):
        """
        Override the parent command's handle() method, adding the password to the new superuser.

        Due to the inflexible way in which contrib.auth's createsuperuser command was written, it
        is not possible to reuse or cleanly override the functionality of the command's handle()
        method without egregious code duplication. If the parent handle() method algorithm changes,
        its functionality will have to be mirrored in this overriding method manually as well.
        createsuperuser's functionality should have been broken out into discrete class methods
        which would allow for sane command class extensions.

        See:
            https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py

        """
        username = None
        password = None

        if not options['password']:
            super().handle(*args, **options)
        else:
            #  # Watch this. Clean handle method in contrast with the monolithic rambling of
            # contrib.auth's.
            if self._get_interactive_mode(**options):
                # Interactive mode.
                pass
            else:
                # Non-interactive mode.
                pass

        # Need to handle invalid password errors from
        #   https://github.com/django/django/blob/master/django/contrib/auth/base_user.py
