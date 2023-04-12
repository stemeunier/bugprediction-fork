import astroid
from astroid.exceptions import InferenceError
from pylint.checkers import BaseChecker
from connectors.pylint.custom_linter import CustomLinter
from utils.math import Math

class CustomAstChecker(BaseChecker):
    """
    CustomAstChecker is a class that inherits from the BaseChecker class of the pylint.checkers module. 
    This class provides methods to visit the nodes of an AST tree and compute various code metrics. 

    Attributes:
        name (str): The name of the checker.
        priority (int): The priority of the checker.
        msgs (dict): A dictionary containing messages to be reported by the checker.
        import_list (set): A set containing the names of imported modules.
        method_data (dict): A dictionary containing the data for each method in a class.
        class_depedency (dict): A dictionary containing the dependency information between classes.
        class_method_rfc (dict): A dictionary containing the method RFC (Response For a Class) for each class.
        class_method_defs (dict): A dictionary containing the definition information of each method in a class.
        class_method_calls (dict): A dictionary containing the call information of each method in a class.
    """

    # These properties have to be defined
    # or the linter fink is a malformed checker
    name = 'class-visitor'
    priority = -1
    msgs = {'R0001': ('Custom checker.', 'Visited', 'CustomAstChecker class.')}

    import_list = set()
    method_data = {}
    class_depedency = {}
    class_method_rfc = {}
    class_method_defs = {}
    class_method_calls = {}
    
    def __init__(self, linter: "CustomLinter" = None) -> None:
        super().__init__(linter)
        self.data = linter.metrics
    
    # Method call on class def visit
    def visit_classdef(self, node : astroid.ClassDef) -> None:
        """
        Visits a ClassDef node and updates various metrics related to the class. 
        Counts the number of classes with docstrings, the number of inner classes 
        and the number of fields. Computes the Depth of Inheritance Tree (DIT) metric for 
        the class hierarchy. Prepares the Coupling Between Objects (CBO) metric for the 
        class. Computes data for the Lack of Cohesion in Methods (LCC) metric. 

        Args:
            node: The ClassDef node to visit.

        Returns:
            None.
        """
        self.count_docstring(node)

        self.data.noc += 1

        # Check if this node is a inner class
        context = node.frame()
        if not isinstance(context.parent, astroid.Module):
            self.data.num_inner_cls_and_lambda += 1
        
        # count number of field
        for child_node in node.get_children():
            # is child field if is form of "var_name = x" or "var_name : type = x"
            if isinstance(child_node, astroid.nodes.Assign) or isinstance(child_node, astroid.nodes.AnnAssign):
                self.data.num_field += 1

        # Compute the DIT
        dit = self.__compute_class_dit(node)
        if (self.data.dit < dit):
            self.data.dit = dit

        # Prepare the cbo
        self.class_depedency[node.name] = set()
        # Increase the cbo with the inherit class
        if len(node.bases):
            # the direct inherit class
            bases_klass_nodes = [next(nodes.infer()) for nodes in node.bases]
            for klass in bases_klass_nodes:
                self.class_depedency[node.name].add(klass.name)

        # Compute data for lcc
        self.class_method_defs[node.name] = set()
        for body in node.body:
            if isinstance(body, astroid.FunctionDef):
                method_name = node.name + "." + body.name
                self.class_method_defs[node.name].add(method_name)
        if node.name not in self.class_method_calls:
            self.class_method_calls[node.name] = set()

    # Method call on function def visit
    def visit_functiondef(self, node: astroid.FunctionDef) -> None:
        """
        The `visit_functiondef` method is called when visiting a function definition node in the AST. 
        It updates the count of the number of functions in the module, and if the function is a method, 
        it visits it using the `visit_methoddef` method. 

        Args:
            node (astroid.FunctionDef): The AST node representing the function definition.

        Returns:
            None
        """
        self.count_docstring(node)
        # is method
        if node.is_method():
            self.visit_methoddef(node)
        # is function
        else:
            self.data.nof += 1

    def visit_methoddef(self, node: astroid.FunctionDef) -> None:
        """
        The visit_methoddef method is called when visiting a method definition node in the AST. 
        It updates the count of the number of methods in the module and prepares data for the fan-out metric.

        Args:
        node (astroid.FunctionDef): The AST node representing the method definition.

        Returns:
        None
        """
        self.data.nom += 1
        
        # Prepare data for fan out
        method_name = node.parent.name + "." + node.name
        if not (method_name in self.method_data):
            self.method_data[method_name] = {"fan_out": 0}

    def visit_import(self, node: astroid.Import) -> None:
        """
        The visit_import method is called when visiting an import statement 
        node in the AST. It adds the imported module to the set of imported modules.

        Args:
        node (astroid.Import): The AST node representing the import statement.

        Returns:
        None
        """
        self.import_list.add(node.names[0][0])

    def visit_importfrom(self, node: astroid.ImportFrom) -> None:
        """
        The visit_importfrom method is called when visiting an import statement 
        with a "from" keyword in the AST. It adds the name of the imported module 
        to the set of imported modules.

        Args:
        node (astroid.ImportFrom): The AST node representing the import from statement.

        Returns:
        None
        """
        self.import_list.add(node.names[0][0])

    def visit_excepthandler(self, node: astroid.ExceptHandler) -> None:
        """
        The visit_excepthandler method is called when visiting an exception 
        handler node in the AST. It increments the count of the number of 
        try-except blocks in the module.

        Args:
        node (astroid.ExceptHandler): The AST node representing the exception handler.

        Returns:
        None
        """
        self.data.num_try_except += 1
        
    def visit_return(self, node: astroid.Return) -> None:
        """
        The visit_return method is called when visiting a return statement 
        node in the AST. It increments the count of the number of return 
        statements in the module.

        Args:
        node (astroid.Return): The AST node representing the return statement.

        Returns:
        None
        """
        self.data.num_returns += 1

    def visit_for(self, node: astroid.For) -> None:
        """
        The visit_for method is called when visiting a for loop node in the AST. 
        It increments the count of loops in the module.

        Args:
        node (astroid.For): The AST node representing the for loop.

        Returns:
        None
        """
        self.data.num_loops += 1

    def visit_while(self, node: astroid.While) -> None:
        """
        The visit_while method is called when visiting a while loop node in the AST. 
        It increments the count of loops in the module.

        Args:
        node (astroid.While): The AST node representing the for loop.

        Returns:
        None
        """
        self.data.num_loops += 1

    def visit_compare(self, node: astroid.Compare) -> None:
        """
        The visit_compare method is called when visiting a comparison node in the AST. 
        It updates the count of the number of comparisons in the module.

        Args:
        node (astroid.Compare): The AST node representing the comparison.

        Returns:
        None
        """
        self.data.num_comparisons += 1

    def visit_binop(self, node: astroid.BinOp) -> None:
        """
        The visit_binop method is called when visiting a binary operation node in the AST. 
        It increments the count of the number of mathematical operations in the module.

        Args:
        node (astroid.BinOp): The AST node representing the binary operation.

        Returns:
        None
        """
        self.data.num_math_op += 1

    def visit_assign(self, node: astroid.Assign) -> None:
        """
        The visit_assign method is called when visiting an assignment node in the AST. 
        It updates the count of the number of variables assigned in the module.

        Args:
        node (astroid.Assign): The AST node representing the assignment.

        Returns:
        None
        """
        self.data.num_variable += 1

    def visit_lambda(self, node: astroid.Lambda) -> None:
        """
        The visit_lambda method is called when visiting a lambda expression node in the AST. It updates the count of the number of inner classes and lambda functions in the module.

        Args:
        node (astroid.Lambda): The AST node representing the lambda expression.

        Returns:
        None
        """
        self.data.num_inner_cls_and_lambda += 1

    def visit_const(self, node: astroid.Const) -> None:
        """
        The visit_const method is called when visiting a constant node in the AST. 
        It updates the count of the number of different types of constants (string literals, 
        numbers, booleans, and NoneType), depending on the type of the constant node.

        Args:
        node (astroid.Const): The AST node representing the constant.

        Returns:
        None
        """
        if node.pytype() == "builtins.bool":
            pass
        elif node.pytype() == "builtins.str":
            self.data.num_str_literals += 1
        elif node.pytype() == "builtins.NoneType":
            pass
        else:
            self.data.num_numbers += 1

    # method call on function call visit
    def visit_call(self, node: astroid.Call) -> None:
        """
        The visit_call method is called when visiting a function call node in the AST. 
        Computes the fan-out. It also gets data for the LCC (Lack of Cohesion in Methods) metric.

        Args:
        node (astroid.Call): The AST node representing the function call.

        Returns:
        None
        """
        # retrieve the context
        context = node.frame()
        # check if the context is in the method
        if isinstance(context, astroid.FunctionDef) and context.is_method():
            # Retrieve the class of the context method
            context_class = context.parent
            context_name = f"{context_class.name}.{context.name}"

            # compute the fan out
            # check if we can store the data or create it
            if context_name not in self.method_data:
                self.method_data[context_name] = {"fan_out": 0}
            self.method_data[context_name]["fan_out"] += 1

        # Get data for lcc
        if isinstance(node.func, astroid.Attribute):
            try:
                called_method_class = next(node.func.expr.infer())
                if called_method_class.name not in self.class_method_calls:
                    self.class_method_calls[called_method_class.name] = set()
                self.class_method_calls[called_method_class.name].add(node.func.attrname)
            except InferenceError:
                # InferenceError can appear in two cases:
                # - the node.func.expr is a non-method FunctionDef call
                # - the node.func.expr is a SubScript node (a sequence)
                # These two cases are not used for the lcc.
                pass

    # method call on module visit
    def visit_module(self, node: astroid.Module) -> None:
        """
        The visit_module method is called when visiting a module node in the AST. 
        It updates the count of the number of docstrings.

        Args:
        node (astroid.Module): The AST node representing the module.

        Returns:
        None
        """
        self.count_docstring(node)
    
    # method call when the visit is complete
    def close(self) -> None:
        """
        The close method is called when the visit to the AST is complete. 
        It computes the final metrics values for the module and updates 
        the data attribute of the CheckerData object.

        Args:
        None

        Returns:
        None
        """
        lcc_values = {}
        self.data.num_import = len(self.import_list)
        self.data.fan_out = Math.get_rounded_mean_safe([method["fan_out"] for method in self.method_data.values()])
        self.data.cbo = Math.get_rounded_mean_safe([len(v) for v in self.class_depedency.values()])
        for class_name in self.class_method_defs:
            called_methods = self.class_method_calls[class_name]
            defined_methods = self.class_method_defs[class_name]
            if len(defined_methods) == 0:
                lcc_values[class_name] = 0.0
            else:
                lcc_values[class_name] = 1.0 - (len(called_methods) / len(defined_methods))
        self.data.lcc = Math.get_rounded_mean_safe(lcc_values.values())

    def count_docstring(self, node: astroid) -> None:
        """
        This method counts the number of docstrings in the given AST node 
        and updates the "num_docstring" field of the MetricsVisitor data 
        attribute accordingly.

        Args:
        node (astroid): An AST node to count the docstrings.

        Returns:
        None
        """
        if node.doc_node:
            self.data.num_docstring += 1

    # Compute the DIT for a simple class
    def __compute_class_dit(self, node: astroid.ClassDef):
        """
        The __compute_class_dit method is used to compute the Depth of Inheritance 
        Tree (DIT) metric for a simple class in the AST. It recursively computes 
        the DIT for each inherited class, and returns the maximum DIT value.

        Args:
        node (astroid.ClassDef): An AST ClassDef node for which to compute the DIT.

        Returns:
        An integer representing the DIT value for the given class node.
        """
        local_dit = 0
        # Compute the dit for each inherit class
        # convert Name nodes to ClassDef nodes
        # We need to interpret the bases names to get the class def node
        bases_klass_nodes = [next(nodes.infer()) for nodes in node.bases]
        for klass in bases_klass_nodes:
            # This condition is for the case "class A(None)"
            if isinstance(klass, astroid.ClassDef):
                klass_dit = self.__compute_class_dit(klass)
                # The DIT of the class is the max DIT of each inherit class
                if klass_dit > local_dit :
                    local_dit = klass_dit
        # The class DIT is the inherit class dit + 1
        return local_dit + 1
