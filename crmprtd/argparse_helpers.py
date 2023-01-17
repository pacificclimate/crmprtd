import sys as _sys
from argparse import Action, SUPPRESS


class OneAndDoneAction(Action):
    """Action subclass that invokes a specified function at time of option execution
    (not at time option definition). The function is passed, as arguments, the arguments
    specified when the option is invoked. This is like a souped-up version of the
    "version" action, with deferred value computed by the function, and arguments
    specified by the user.

    WARNING: This poses a security risk if you do something incautious with the
    arguments.
    """
    def __init__(self, option_strings, dest, function=None, default=SUPPRESS, **kwargs):
        super().__init__(option_strings, dest=dest, default=default, **kwargs)
        self.function = function

    def __call__(self, parser, namespace, values, option_string=None):
        formatter = parser._get_formatter()
        formatter.add_text(str(self.function(*values)))
        parser._print_message(formatter.format_help(), _sys.stdout)
        parser.exit()
