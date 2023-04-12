from pylint.lint import PyLinter

from connectors.pylint.checker_data import CheckerData

class CustomLinter(PyLinter):
    """
    A custom PyLinter that inherits from PyLinter and adds a metrics attribute of type CheckerData. 

    :param reporter: A reporter object that inherits from BaseReporter and will handle the messages reported by the linter.
    :type reporter: BaseReporter
    """
    def __init__(self, reporter):
        super().__init__(reporter=reporter)
        self.metrics = CheckerData()