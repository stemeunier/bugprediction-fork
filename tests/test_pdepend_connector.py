import unittest
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock

from connectors.pdepend import PDependConnector

class TestPDependConnector(unittest.TestCase):

    def setUp(self):
        self.report_path = "./tests/mocks/pdepend_summary.xml"
        self.version_id = 2

        self.directory = 'test_directory'
        self.version = MagicMock(version_id=self.version_id)
        self.session = MagicMock()
        self.config = {'language': 'PHP'}
        self.pdepend_connector = PDependConnector(self.directory, self.version, self.session, self.config)

    def test_xml_get_nodes_atribute_existing(self):
        """
        Test of retrieving values in the XML from existing nodes and attributes
        """
        xml_tree = ET.parse(self.report_path)
        xml_root = xml_tree.getroot()
        package_noc = self.pdepend_connector._xml_get_nodes_atribute(xml_root, "package", "noc")
        self.assertEqual(package_noc, ["3", "5", "7", "4"])
        class_wmc = self.pdepend_connector._xml_get_nodes_atribute(xml_root, "class", "wmc")
        self.assertEqual(class_wmc, ["3", "3", "2", "6", "2", "2", "5", "2", "5", "123", "76", "36", "32", "13", "11", "1", "4", "5", "3"])

    def test_xml_get_nodes_atribute_not_existing(self):
        """
        Test of retrieving values in the XML from non-existing nodes and attributes
        """
        xml_tree = ET.parse(self.report_path)
        xml_root = xml_tree.getroot()
        package_noc = self.pdepend_connector._xml_get_nodes_atribute(xml_root, "package", "jcjfdbxj")
        self.assertEqual(package_noc, [])
        class_wmc = self.pdepend_connector._xml_get_nodes_atribute(xml_root, "ldjhhs", "wmc")
        self.assertEqual(class_wmc, [])


    def test_invalid_list_str_to_int(self):
        list_str = ["3", "djcnsn", "7", "4"]
        with self.assertRaises(ValueError):
            self.pdepend_connector._list_str_to_int(list_str)

    def test_compute_metrics(self):
        metric = MagicMock()
        metric = self.pdepend_connector.compute_metrics(metric, self.report_path)

        self.assertEqual(metric.version_id, self.version_id)
        self.assertEqual(metric.pdepend_cbo, 5.09)
        self.assertEqual(metric.pdepend_fan_out, 5.95)
        self.assertEqual(metric.pdepend_dit, 1)
        self.assertEqual(metric.pdepend_nof, 1)
        self.assertEqual(metric.pdepend_noc, 4.75)
        self.assertEqual(metric.pdepend_nom, 7.84)
        self.assertEqual(metric.pdepend_nopm, 4.91)
        self.assertEqual(metric.pdepend_vars, 3.41)
        self.assertEqual(metric.pdepend_wmc, 17.32)
        self.assertEqual(metric.pdepend_calls, 4.44)
        self.assertEqual(metric.pdepend_nocc, 0.16)
        self.assertEqual(metric.pdepend_noom, 0.05)
        self.assertEqual(metric.pdepend_noi, 0.25)
        self.assertEqual(metric.pdepend_nop, 5)

if __name__ == '__main__':
    unittest.main()