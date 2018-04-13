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
import django.core.exceptions
import django.core.management.base


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

    def get_raw_input(self, message, default=None):
        """
        Solicit input from the user, falling back to a default value if necessary.

        Replaces super().get_input_data() for two reasons: 1) get_input_data() actually performs
        validation and type coercion on received input by calling Field.clean(value, None), and 2)
        get_input_data is an annoying name.

        Args:
            message (str): The input prompt message to be printed to stdout.
            default (str): The default value to return if the received input is empty.

        Returns:
            str: The received input or the default value if the prerequisite conditions were met.

        See:
            https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
                Command.get_input_data()

        """
        raw_input = input(message)
        if default and raw_input == '':
            raw_input = default

        return raw_input

    def _get_username_prompt_text(self, default_username=None):
        """
        Generate the string for the username prompt issued in interactive mode.

        The instance attributes used are defined in the parent Command class' __init__() method.

        Args:
            default_username (str): The default username that can optionally be used if empty input
                is received.

        Returns:
            str: The specialized username prompt string to be displayed to user in interactive mode
                if the username option was not passed to the command on initial call.

        See:
            https://github.com/django/django/blob/master/django/contrib/auth/management/__init__.py

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

        Args:
            args (sequence): The positional argument tuple that was passed to the management command
                handle() method. Unsurprisingly, Django provides no information, neither in the
                documentation nor in source code doc blocks or comments, about what is contained in
                the args parameter to the handle() method. I have not yet seen management command
                code that makes use of this parameter.
            options (dict): The same dictionary of options passed to the command invocation.
                Identical to the options paramater declared by self.handle().

        Returns:
            str: The output, if any, of the command. In the case of this command, most output is
                written directly to stdout or stderr.

        See:
            https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#django.core.management.BaseCommand.handle

        """
        # Get username.
        username = options[self.UserModel.USERNAME_FIELD]
        if username is not None:
            error_messages = self._validate_username(username)
            if error_messages:
                raise django.core.management.base.CommandError(
                    '; '.join(error_messages)
                )
        else:
            username = self._prompt_valid_username()

        # Get password.
        # Get required_fields.
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

    def _prompt_valid_username(self):
        """
        Solicit input from the user in a loop until a valid username value is received.

        Default username is ultimately generated by the Python standard library getpass.getuser().
        See docs page for details.

        Returns:
            str: A valid username value.

        See:
                https://docs.python.org/3/library/getpass.html

        """
        default_username = django.contrib.auth.management.get_default_username()
        prompt_message = self._get_username_prompt_text(default_username=default_username)
        username = None

        while username is None:
            username_raw_input = self.get_raw_input(prompt_message, default_username)
            error_messages = self._validate_username(username_raw_input)
            if error_messages:
                self.stderr.write('Error: {!s}'.format('; '.join(error_messages)))
            else:
                username = username_raw_input

        return username

    def _validate_input(self, field, value):
        """
        Validate a received input value against the corresponding model field's validation methods.

        Args:
            field (django.db.models.Field): A model field instance against which to validate the
                input value.
            value (str): The received input value to validate.

        Returns:
            sequence: An unordered sequence of error messages. If the sequence is empty, then the
                input value passed all validation checks.

        See:
            https://github.com/django/django/blob/master/django/db/models/fields/__init__.py

        """
        error_messages = set()
        try:
            field.clean(value, None)
        except django.core.exceptions.ValidationError as e:
            error_messages.update(e.messages)

        return error_messages

    def _validate_username(self, username):
        """
        Validate a potential username value received as input.

        Not only is the username value validated against the username field, but it a preliminary
        username uniqueness check is also executed if the username field's "unique" attribute is
        set to True.

        Args:
            username (str): The username value to be validated.

        Returns:
            sequence: An unordered sequence of error messages. If the sequence is empty, then the
                username value passed all validation checks.

        See:
            https://github.com/django/django/blob/master/django/db/models/base.py

        """
        error_messages = self._validate_input(self.username_field, username)

        test_user_instance = self.UserModel(**{self.UserModel.USERNAME_FIELD: username})
        try:
            test_user_instance.validate_unique()
        except django.core.exceptions.ValidationError as e:
            error_messages.update(e.messages)

        return error_messages

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
