import unittest

from unittest.mock import MagicMock, Mock
from connectors.radon import RadonConnector
from radon.visitors import Function, Class

from utils.proglang import is_python_file


class TestRadonConnector(unittest.TestCase):
    def setUp(self):
        self.directory = 'test_directory'
        self.version = MagicMock()
        self.session = MagicMock()
        self.config = {'language': 'python'}
        self.radon_connector = RadonConnector(self.directory, self.version, self.session, self.config)

    def test_compute_cc_metrics_with_function_metrics(self):
        cc_metrics = [Function('function_name', 1, 1, 10, False, "class_nam", [], 5)]
        self.radon_connector._RadonConnector__compute_cc_metrics(cc_metrics)
        self.assertEqual(self.radon_connector.noc, [0])
        self.assertEqual(self.radon_connector.nom, [0])
        self.assertEqual(self.radon_connector.nof, [1])
        self.assertEqual(self.radon_connector.class_loc, [])
        self.assertEqual(self.radon_connector.func_loc, [9])
        self.assertEqual(self.radon_connector.method_loc, [])
        self.assertEqual(self.radon_connector.cc, [5])

    def test_compute_cc_metrics_with_class_metrics(self):
        cc_metrics = [Class('class_name', 1, 0, 11, [Function('function_name', 1, 1, 10, True, "class_name", [], 5)], [], 6)]
        self.radon_connector._RadonConnector__compute_cc_metrics(cc_metrics)
        self.assertEqual(self.radon_connector.noc, [1])
        self.assertEqual(self.radon_connector.nom, [1])
        self.assertEqual(self.radon_connector.nof, [0])
        self.assertEqual(self.radon_connector.class_loc, [10])
        self.assertEqual(self.radon_connector.func_loc, [])
        self.assertEqual(self.radon_connector.method_loc, [9])
        self.assertEqual(self.radon_connector.cc, [6])

    def test_compute_cc_metrics_with_unsupported_metrics(self):
        cc_metrics = ['unsupported_metric']
        with self.assertRaises(TypeError):
            self.radon_connector._RadonConnector__compute_cc_metrics(cc_metrics)

    def test_compute_raw_metrics_with_supported_metrics(self):
        raw_metrics = Mock(loc=10, lloc=20, sloc=30, comments=40, multi=50, blank=60, single_comments=70)
        self.radon_connector._RadonConnector__get_raw_metrics(raw_metrics)
        self.assertEqual(self.radon_connector.loc, [10])
        self.assertEqual(self.radon_connector.lloc, [20])
        self.assertEqual(self.radon_connector.sloc, [30])
        self.assertEqual(self.radon_connector.comments, [40])
        self.assertEqual(self.radon_connector.docstring, [50])
        self.assertEqual(self.radon_connector.blank, [60])
        self.assertEqual(self.radon_connector.single_comment, [70])

    def test_compute_raw_metrics_with_unsupported_metrics(self):
        raw_metrics = {}
        with self.assertRaises(TypeError):
            self.radon_connector._RadonConnector__get_raw_metrics(raw_metrics)

    def test_is_python_file_true(self):
        result = is_python_file("example.py")
        self.assertTrue(result)

    def test_is_python_file_false(self):
        result = is_python_file("example.txt")
        self.assertFalse(result)
    
    
    def test_calcule_wmc_metric_with_class_metrics(self):
        cc_metrics = [Class('class_name', 1, 0, 11, [Function('function_name', 1, 1, 10, True, "class_name", [], 5)], [], 6)]
        self.radon_connector._RadonConnector__calcule_wmc_metric(cc_metrics)
        self.assertEqual(self.radon_connector.wmc, [5])

    def test_calcule_wmc_metric_with_multiple_classes(self):
        cc_metrics = [
            Class('class_name1', 1, 0, 11, [Function('function_name1', 1, 1, 10, True, "class_name1", [], 5)], [], 6),
            Class('class_name2', 1, 0, 11, [Function('function_name2', 1, 1, 10, True, "class_name2", [], 10),
                                            Function('function_name3', 1, 1, 10, True, "class_name2", [], 5)], [], 6)
        ]
        self.radon_connector._RadonConnector__calcule_wmc_metric(cc_metrics)
        self.assertEqual(self.radon_connector.wmc, [5, 7.5])

    def test_calcule_wmc_metric_with_no_methods(self):
        cc_metrics = [Class('class_name', 1, 0, 11, [], [], 6)]
        self.radon_connector._RadonConnector__calcule_wmc_metric(cc_metrics)
        self.assertEqual(self.radon_connector.wmc, [0])
            
if __name__ == '__main__':
    unittest.main()
