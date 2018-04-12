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
import sys

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

    The contrib.auth implementation of createsuperuser is monolithic and inflexible. Since virtually
    all of its behavior is defined in a single method, one is unable to selectively override aspects
    of its behavior and one is instead forced to reimplement the entire handle() method. I have
    attempted to correct this by following proper coding standards and breaking the logic into
    discrete methods, forming an overridable/extendable and cohesive class.

    """

    def _exit_with_error(self, code=1, message=None):
        """
        Output message to stderr and exit with non-zero code.

        Args:
            code (int): The exit code.
            message (str): The message to output to stderr.

        """
        if message is not None:
            self.stderr.write(message)
        sys.exit(code)

    def _get_interactive_mode(self, **options):
        """
        Determine if this command is running in interactive mode.

        Interactive mode is primarily determined by the --noinput flag, the value of which is saved
        in the "interactive" variable. The value defaults to True but, if --noinput is
        present, the value of "interactive" will be set to False. The parent contrib.auth command
        will ignore the calling environment with regards to determining whether to run interactively
        or noninteractively and will only check for I/O capability if "interactive" is True.

        The "interactive" option is added in contrib.auth's createsuperuser Command class. It is a
        flag with the argparse action "store_false". However, "interactive" can be forced to contain
        a value by passing a kwarg through django.core.management.call_command() as it bypasses
        the argparse argument parsing.

        See:
            https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
            https://docs.python.org/3/library/argparse.html#action

        Note self.stdin is defined in the parent's Command.execute() method.

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
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#django.core.management.BaseCommand.handle
            https://docs.python.org/3/library/sys.html#sys.stdin
            https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
                django.contrib.auth.management.commands.createsuperuser.Command.add_arguments()

        """
        interactive_option = options.get('interactive', False)
        interactive_tty_session = (hasattr(self.stdin, 'isatty') and self.stdin.isatty())

        if interactive_option and not interactive_tty_session:
            raise django.contrib.auth.management.commands.createsuperuser.NotRunningInTTYException(
                'Not running in a TTY.'
            )

        return interactive_option

    def _get_username_prompt_text(self, default_username=None):
        """
        Generate the string for the username prompt issued in interactive mode.

        Default username is ultimately generated by the Python standard library getpass.getuser().
        See docs page for details.

        The instance attributes used are defined in the parent Command class' __init__() method.

        Args:
            default_username (str): The default username that can optionally be used if empty input
                is received.

        Returns:
            str: The specialized username prompt string to be displayed to user in interactive mode
                if the username option was not passed to the command on initial call.

        See:
            https://github.com/django/django/blob/master/django/contrib/auth/management/__init__.py
            https://docs.python.org/3/library/getpass.html

        """
        prompt_string = self.username_field.verbose_name.capitalize()
        if default_username is not None:
            prompt_string += " (leave blank to use '{!s}')".format(default_username)
        if self.username_field.remote_field:
            prompt_string += ' {!s}.{!s}'.format(
                self.username_field.remote_field.model._meta.object_name,
                self.username_field.remote_field.field_name
            )
        prompt_string += ':'

        return prompt_string

    def _handle_interactive(self, *args, **options):
        """
        Handle the overridden command logic under INTERACTIVE conditions.

        Note that blank usernames and username uniqueness handled by get_input_data() calling
        Field.clean(). Currently, get_input_data() will not raise an exception but will write the
        message to stderr and return None.

        Args:
            args (sequence): The positional argument tuple that was passed to the management command
                handle() method. Unsurprisingly, Django provides no information, neither in the
                documentation nor in source code doc blocks or comments, what is contained in the
                args parameter to the handle() method. I have not yet seen management command code
                that makes use of this parameter.
            options (dict): The same dictionary of options passed to the command invocation.
                Identical to the options paramater declared by self.handle().

        Returns:
            str: The output, if any, of the command. In the case of this command, most output is
                written directly to stdout.

        See:
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#django.core.management.BaseCommand.handle

        """
        # Determine username.
        username = options[self.UserModel.USERNAME_FIELD]
        if username is None:
            # Extra conditional used to avoid calling get_default_username() unnecessarily.
            # Will return empty string on failure to determine default username.
            default_username = django.contrib.auth.management.get_default_username()
            while username is None:
                username = self._prompt_for_username(default_username=default_username)

        # get password
        # get required_fields
        # Catch IntegrityError in save method. ValidationError as well?
        pass

    def _handle_noninteractive(self, *args, **options):
        """
        Handle the overridden command logic under NONINTERACTIVE conditions.

        Args:
            args (sequence): The positional argument tuple that was passed to the management command
                handle() method. Unsurprisingly, Django provides no information, neither in the
                documentation nor in source code doc blocks or comments, what is contained in the
                args parameter to the handle() method. I have not yet seen management command code
                that makes use of this parameter.
            options (dict): The same dictionary of options passed to the command invocation.
                Identical to the options paramater declared by self.handle().

        Returns:
            str: The output, if any, of the command. In the case of this command, most output is
                written directly to stdout.

        See:
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#django.core.management.BaseCommand.handle

        """
        pass

    def _prompt_for_username(self, default_username=None):
        """
        Interactively prompt user for super user's username.

        Note that the parent Command's get_input_data() method runs input through the field's
        validation methods by calling its clean() method.

        Args:
            default_username (str): The default username that can optionally be used if empty input
                is received. Used to compose the input prompt message.

        Returns:
            str: The username of the new superuser.

        """
        prompt_message = self._get_username_prompt_text(default_username=default_username)
        username = self.get_input_data(self.username_field, prompt_message, default_username)

        return username

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
        if not options['password']:
            super().handle(*args, **options)
        else:
            try:
                interactive_mode = self._get_interactive_mode(**options)
            except django.contrib.auth.management.commands.createsuperuser.NotRunningInTTYException:
                self._exit_with_error(
                    message='Interactive superuser creation skipped due to not running in a TTY.'
                )

            if interactive_mode:
                try:
                    self._handle_interactive(*args, **options)
                except KeyboardInterrupt:
                    self._exit_with_error(message='\nOperation cancelled.')
            else:
                self._handle_noninteractive(*args, **options)

    def _prompt_for_password(self):
        """
        Need to handle invalid password errors from
        https://github.com/django/django/blob/master/django/contrib/auth/base_user.py
        See https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py

        """
        pass
