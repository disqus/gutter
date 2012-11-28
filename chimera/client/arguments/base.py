class Base(object):
    """
    Base class for Arguments, which are responsible for understanding inputs
    and returning Argument Variables.  Argument variables are compared against
    the Operator inside of a Condition, for deciding if a condition applies to
    the specified input.
    """

    @classmethod
    def applies_to(cls, input):
        """
        Informs users of argument if it applies to the specified input.  By
        default, returns False.
        """
        return False
