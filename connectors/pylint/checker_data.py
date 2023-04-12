

class CheckerData:
    """
    Class for storing the metrics data for a single code file. 
    The class includes various attributes for storing the metrics values for 
    different code quality metrics.

    Attributes:
        cbo (float): Coupling between objects metric value.
        fan_out (float): Fan-out metric value.
        dit (float): Depth of inheritance tree metric value.
        noc (int): Number of children metric value.
        nom (int): Number of methods metric value.
        nof (int): Number of functions metric value.
        num_field (int): Number of fields metric value.
        num_returns (int): Number of return statements metric value.
        num_loops (int): Number of loop statements metric value.
        num_comparisons (int): Number of comparison operators metric value.
        num_try_except (int): Number of try-except statements metric value.
        num_str_literals (int): Number of string literals metric value.
        num_numbers (int): Number of numeric literals metric value.
        num_math_op (int): Number of math operations metric value.
        num_variable (int): Number of variables metric value.
        num_inner_cls_and_lambda (int): Number of inner classes and lambdas metric value.
        num_docstring (int): Number of docstrings metric value.
        num_module (int): Number of modules metric value.
        num_import (int): Number of import statements metric value.
        lcc (float): Lack of cohesion in methods metric value.

    Methods:
        __str__(): Returns a string representation of the object, showing all non-callable attributes and their values.
    """
    cbo : float = 0
    # fan_in : float = 0
    fan_out : float = 0
    dit : float = 0
    noc : int = 0
    nom : int = 0
    nof : int = 0
    num_field : int = 0
    num_returns : int = 0
    num_loops : int = 0
    num_comparisons : int = 0
    num_try_except : int = 0
    # num_parenth_exps : int = 0
    num_str_literals : int = 0
    num_numbers : int = 0
    num_math_op : int = 0
    num_variable : int = 0
    # num_nested_blocks : int = 0
    num_inner_cls_and_lambda : int = 0
    # num_unique_words : int = 0
    # num_log_stmts : int = 0
    num_docstring : int = 0
    num_module : int = 0
    num_import : int = 0
    # nosi : int = 0
    # rfc : float = 0
    # wmc : float = 0 # can be computed by radon
    lcc : float = 0
    # lcom : int = 0

    def __str__(self):
        attributes = []
        for name in dir(self):
            if not name.startswith("__"):
                value = getattr(self, name)
                if not callable(value):
                    attributes.append(f"{name}={value}")
        return f"{self.__class__.__name__}({', '.join(attributes)})"   