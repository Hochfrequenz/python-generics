"""
This a docstring for the module.
"""


class MyClass:  # pylint: disable=too-few-public-methods
    """
    This is a docstring for the class.
    """

    def __init__(self):
        """
        Initialize for the sake of initializing
        """
        self.my_instance_var: str = "abc"

    def do_something(self) -> str:
        """
        Actually does nothing.
        :return: the value of an instance variable
        """
        # this is a super long line with: 100 < line length <= 120 to demonstrate the purpose of pyproject.toml
        return self.my_instance_var
