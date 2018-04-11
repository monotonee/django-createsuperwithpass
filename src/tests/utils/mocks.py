"""
A module containing general testing utilities.

"""

class InputMock:
    """
    Functor mock for the built-in function input().

    Algorithm inspired by Django's tests.auth_tests.test_management.mock_inputs() decorator.
    Attempting to import mock_input from the test_management module has one or more side effects and
    raises a RuntimeError, so I'm simply defining my own implementation here.

    Django's mock_inputs() attempts to re-implement what unittest.mock aleady does. I find that
    extremely perplexing but unsurprising given my knowledge of Django's coding style. This class is
    instead designed to work with unittest.mock.

    Also note that Django's tests works with an additional layer of mapping in
    MOCK_INPUT_KEY_TO_PROMPTS, which attempts to map the verbose, literal user prompt strings to
    generic "input keys" or input data categories. However, in typical Django fashion, the prompt
    "input key" is not ALWAYS used in practice, meaning that Django's mock_input() must check BOTH
    the "input key" and the literal prompt. Sigh. Regardess, given the low number of tests in the
    project, I don't currently consider "input keys" necessary.

    See:
        https://github.com/django/django/blob/master/tests/auth_tests/test_management.py
        https://docs.python.org/3/library/functions.html#input
        https://docs.python.org/3/reference/datamodel.html#object.__call__

    """

    def __init__(self, prompt_map):
        """
        Initialize the class instance.

        Args:
            prompt_map (dict): A dictionary, the keys of which are prompt strings and the values
                of which are the values to be returned to the calling script that is awaiting input.
                Essentially, a mapping of input prompts to user responses.

        """
        self._prompt_map = prompt_map
        self._prompts_received = set()

    def _get_prompt_response(self, prompt):
        prompt_response = None

        for prompt_classifier_func, prompt_class_response in self._prompt_map.items():
            if prompt_classifier_func(prompt):
                prompt_response = prompt_class_response

        return prompt_response


    def __call__(self, prompt=None):
        """
        Mimic the built-in input() behavior and return a string for a given prompt.

        Looks up the prompt string from the prompt map and, if found, returns the corresponding
        string.

        Args:
            prompt (str): The optional prompt for the input() call. Identical to the prompt argument
                of the built-in input().

        Returns:
            str: The mock "input" from the "user".

        See:
            https://docs.python.org/3/library/functions.html#input
            https://docs.python.org/3/reference/datamodel.html#object.__call__

        """
        self._prompts_received.add(prompt)
        response = self._get_prompt_response(prompt)
        if response is None:
            raise ValueError('Mock input for {!r} not found.'.format(prompt))

        return response
