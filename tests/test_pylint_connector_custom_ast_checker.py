

from ast import FunctionDef
import unittest
from unittest.mock import MagicMock, Mock, patch

import astroid
from connectors.pylint.checker_data import CheckerData

from connectors.pylint.custom_ast_checker import CustomAstChecker
from connectors.pylint.custom_linter import CustomLinter


class TestPylintConnector(unittest.TestCase):

    def setUp(self) -> None:
        self.checker_data = CheckerData()
        self.linter = Mock()
        self.linter.metrics = self.checker_data
        self.custom_ast_checker = CustomAstChecker(self.linter)
        self.custom_ast_checker.class_depedency = {}
        self.custom_ast_checker.class_method_defs = {}
        self.custom_ast_checker.class_method_calls = {}

    def test_visit_classdef_counts_docstrings(self):
        node = astroid.parse('''
            class MyClass:
                \"\"\"MyClass docstring\"\"\"
                pass
        ''').body[0]
        with patch.object(self.custom_ast_checker, 'count_docstring') as mock_count_docstring:
            self.custom_ast_checker.visit_classdef(node)

        mock_count_docstring.assert_called_once_with(node)

    # DO TO count classdef in method
    def test_visit_classdef_counts_inner_classes(self):
        node = astroid.parse('''
            class MyClass:
                class InnerClass:
                    pass
                def method(self):
                    class InnerInnerClass:
                        pass
        ''').body[0]
        self.custom_ast_checker.visit_classdef(node) # give MyCLass to the visitor
        self.custom_ast_checker.visit_classdef(node.body[0]) # give InnerClass to the visitor
        self.custom_ast_checker.visit_classdef(node.body[1].body[0]) # give InnerInnerClass to the visitor
        self.assertEqual(self.custom_ast_checker.data.num_inner_cls_and_lambda, 2)

    def test_visit_classdef_counts_fields(self):
        node = astroid.parse('''
            class MyClass:
                x = 1
                y: int = 2
                def method(self):
                    z = 3
        ''').body[0]
        self.custom_ast_checker.visit_classdef(node)
        self.assertEqual(self.custom_ast_checker.data.num_field, 2)

    def test_visit_classdef_computes_dit(self):
        node1 = astroid.parse('''
            class A:
                pass
            class B(A):
                pass
            class C(B):
                pass
        ''').body[1]
        self.custom_ast_checker.visit_classdef(node1)
        self.assertEqual(self.custom_ast_checker.data.dit, 2)

    def test_visit_classdef_prepares_cbo(self):
        node = astroid.parse('''
            class A:
                pass
            class B(A):
                pass
        ''')
        self.custom_ast_checker.visit_classdef(node.body[0])
        self.custom_ast_checker.visit_classdef(node.body[1])
        self.assertDictEqual(self.custom_ast_checker.class_depedency, {'A': set(), 'B': {'A'}})

    def test_visit_classdef_computes_lcc(self):
        node = astroid.parse('''
            class MyClass:
                def method1(self):
                    pass
                def method2(self):
                    self.method1()
        ''').body[0]
        self.custom_ast_checker.visit_classdef(node)
        self.assertDictEqual(self.custom_ast_checker.class_method_defs, {'MyClass': {'MyClass.method1', 'MyClass.method2'}})
        self.assertDictEqual(self.custom_ast_checker.class_method_calls, {'MyClass': set()})

    def test_visit_functiondef_count_nof(self):
        # create a mock FunctionDef node
        node = astroid.parse('''
            def function1():
                pass
        ''').body[0]
        # call the visit_functiondef method
        self.custom_ast_checker.visit_functiondef(node)
        # check that self.data.nof has been incremented by 1
        self.assertEqual(self.custom_ast_checker.data.nof, 1)

    def test_visit_functiondef_visit_methoddef(self):
        # create a mock FunctionDef node
        node = astroid.parse('''
            class MyClass:
                def method1(self):
                    pass
        ''').body[0].body[0]
        with patch.object(self.custom_ast_checker, 'visit_methoddef') as mock_visit_methoddef:
            self.custom_ast_checker.visit_functiondef(node)
        # check that the visit_methoddef method has been called once
        mock_visit_methoddef.assert_called_once_with(node)

    def test_visit_methoddef(self):
        node = astroid.parse('''
            class MyClass:
                def my_method(self):
                    pass
        ''').body[0].body[0]
        before = self.custom_ast_checker.data.nom
        self.custom_ast_checker.visit_methoddef(node)
        after = self.custom_ast_checker.data.nom
        self.assertEqual(after, before+1)

    def test_fan_out_data_initialized(self):
        node = astroid.parse('''
            class MyClass:
                def my_method(self):
                    pass
        ''').body[0].body[0]
        method_name = node.parent.name + "." + node.name
        self.custom_ast_checker.visit_methoddef(node)
        self.assertIn(method_name, self.custom_ast_checker.method_data)
        self.assertEqual(self.custom_ast_checker.method_data[method_name], {"fan_out": 0})

    def test_visit_import(self):
        # Create a MagicMock object for the astroid.Import node
        node = astroid.parse('''
            import os
        ''').body[0]

        # Call the visit_import method with the mocked node
        self.custom_ast_checker.visit_import(node)

        # Check that the imported module has been added to the import list
        self.assertIn("os", self.custom_ast_checker.import_list)

    def test_import_from_adds_module_to_import_list(self):
        node = astroid.parse("""
            from math import sin
        """).body[0]
        self.custom_ast_checker.visit_importfrom(node)
        self.assertIn('sin', self.custom_ast_checker.import_list)

    def test_visit_excepthandler(self):
        node = astroid.parse('''
            try:
                pass
            except Exception as e:
                pass
        ''').body[0].handlers[0]
        self.custom_ast_checker.visit_excepthandler(node)
        self.assertEqual(self.custom_ast_checker.data.num_try_except, 1)

    def test_visit_return(self):
        node = astroid.parse('''
            return 
        ''').body[0]
        self.custom_ast_checker.visit_return(node)
        self.assertEqual(self.custom_ast_checker.data.num_returns, 1)

    def test_visit_for(self):
        node = astroid.parse('''
            for a in range(10):
                pass
        ''').body[0]
        self.custom_ast_checker.visit_for(node)
        self.assertEqual(self.custom_ast_checker.data.num_loops, 1)

    def test_visit_while(self):
        node = astroid.parse('''
            while True:
                pass
        ''').body[0]
        self.custom_ast_checker.visit_while(node)
        self.assertEqual(self.custom_ast_checker.data.num_loops, 1)

    def test_visit_compare(self):
        node = astroid.parse('''
            0 == 1
        ''').body[0]
        self.custom_ast_checker.visit_compare(node)
        self.assertEqual(self.custom_ast_checker.data.num_comparisons, 1)

    def test_visit_binop(self):
        node = astroid.parse('''
            1 + 1
        ''').body[0]
        self.custom_ast_checker.visit_binop(node)
        self.assertEqual(self.custom_ast_checker.data.num_math_op, 1)

    def test_visit_assign(self):
        node = astroid.parse('''
            a = 1
        ''').body[0]
        self.custom_ast_checker.visit_assign(node)
        self.assertEqual(self.custom_ast_checker.data.num_variable, 1)

    def test_visit_lambda(self):
        node = astroid.parse('''
            lambda: print(1 + 1)
        ''').body[0]
        self.custom_ast_checker.visit_lambda(node)
        self.assertEqual(self.custom_ast_checker.data.num_inner_cls_and_lambda, 1)

    def test_visit_const(self):
        node = astroid.parse('''
            1
        ''').body[0].value
        self.custom_ast_checker.visit_const(node)
        self.assertEqual(self.custom_ast_checker.data.num_numbers, 1)
        self.assertEqual(self.custom_ast_checker.data.num_str_literals, 0)

        node = astroid.parse('''
            1.0
        ''').body[0].value
        self.custom_ast_checker.visit_const(node)
        self.assertEqual(self.custom_ast_checker.data.num_numbers, 2)
        self.assertEqual(self.custom_ast_checker.data.num_str_literals, 0)

        node = astroid.parse('''
            1
            \"1\"
        ''').body[1].value
        self.custom_ast_checker.visit_const(node)
        self.assertEqual(self.custom_ast_checker.data.num_numbers, 2)
        self.assertEqual(self.custom_ast_checker.data.num_str_literals, 1)

        node = astroid.parse('''
            True
        ''').body[0].value
        self.custom_ast_checker.visit_const(node)
        self.assertEqual(self.custom_ast_checker.data.num_numbers, 2)
        self.assertEqual(self.custom_ast_checker.data.num_str_literals, 1)

    def test_visit_call(self):
        node = astroid.parse("""
            class MyClass:
                def my_method(self):
                    called = self.my_function()
            
                def my_function():
                    pass
        """)
        class_node = node.body[0]
        method_node = class_node.body[0]
        called_method_node = class_node.body[1]
        call_node = method_node.body[0].value

        context_call_name = f"{class_node.name}.{method_node.name}"

        self.custom_ast_checker.visit_call(call_node)

        self.assertIn(context_call_name, self.custom_ast_checker.method_data)
        self.assertEqual(self.custom_ast_checker.method_data[context_call_name], {'fan_out': 1})
        self.assertIn(class_node.name, self.custom_ast_checker.class_method_calls)
        self.assertEqual(self.custom_ast_checker.class_method_calls[class_node.name], {called_method_node.name})

    def test_close_updates_num_import(self):
        # given
        self.custom_ast_checker.import_list = ["os", "re", "math"]
        # when
        self.custom_ast_checker.close()
        # then
        self.assertEqual(self.custom_ast_checker.data.num_import, 3)

    def test_close_computes_fan_out(self):
        # given
        self.custom_ast_checker.method_data = {
            "MyClass.my_method_1": {"fan_out": 2},
            "MyClass.my_method_2": {"fan_out": 3},
            "AnotherClass.another_method_1": {"fan_out": 1},
            "AnotherClass.another_method_2": {"fan_out": 4}
        }
        # when
        self.custom_ast_checker.close()
        # then
        self.assertEqual(self.custom_ast_checker.data.fan_out, 2.5)

    def test_close_computes_cbo(self):
        # given
        self.custom_ast_checker.class_depedency = {
            "MyClass": {"ClassA", "ClassB", "ClassC"},
            "AnotherClass": {"ClassD", "ClassE"}
        }
        # when
        self.custom_ast_checker.close()
        # then
        self.assertEqual(self.custom_ast_checker.data.cbo, 2.5)

    def test_close_computes_lcc(self):
        # given
        self.custom_ast_checker.class_method_defs = {
            "MyClass": {"my_method_1", "my_method_2", "my_method_3"},
            "AnotherClass": {"another_method_1", "another_method_2"}
        }
        self.custom_ast_checker.class_method_calls = {
            "MyClass": {"my_method_1", "my_method_2"},
            "AnotherClass": {"another_method_1"}
        }
        # when
        self.custom_ast_checker.close()
        # then
        self.assertEqual(self.custom_ast_checker.data.lcc, 0.42)

    def test_close_empty_class_method_defs(self):
        # given
        self.custom_ast_checker.class_method_defs = {
            "MyClass": set(),
            "AnotherClass": {"another_method_1", "another_method_2"}
        }
        self.custom_ast_checker.class_method_calls = {
            "MyClass": {"my_method_1", "my_method_2"},
            "AnotherClass": {"another_method_1"}
        }
        # when
        self.custom_ast_checker.close()
        # then
        self.assertEqual(self.custom_ast_checker.data.lcc, 0.25)

    def test_compute_class_dit_with_simple_class(self):
        # Define a simple class without inheritance
        node = astroid.parse("""
            class MyClass:    
                pass
        """).body[0]
        dit = self.custom_ast_checker._CustomAstChecker__compute_class_dit(node)
        self.assertEqual(dit, 1)

    def test_compute_class_dit_with_single_level_inheritance(self):
        # Define a class inheriting from a simple class
        node = astroid.parse("""
            class Parent:
                pass
            class Child(Parent):
                pass
        """).body[1]
        dit = self.custom_ast_checker._CustomAstChecker__compute_class_dit(node)
        self.assertEqual(dit, 2)

    def test_compute_class_dit_with_multi_level_inheritance(self):
        # Define a class inheriting from a class inheriting from a simple class
        node = astroid.parse("""
            class Grandparent:
                pass
            class NoHerit:
                pass
            class Parent(Grandparent):
                pass
            class Child(NoHerit, Parent):
                pass
        """).body[3]
        dit = self.custom_ast_checker._CustomAstChecker__compute_class_dit(node)
        self.assertEqual(dit, 3)
    
    
    


    