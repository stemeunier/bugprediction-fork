import unittest
from unittest.mock import MagicMock, Mock, patch
from models.metric import Metric
from connectors.pylint.pylint import PylintConnector

class TestPylintConnector(unittest.TestCase):

    test_directory = "./tests/mocks/"

    def setUp(self):
        self.config = MagicMock(language= 'python')
        self.version = MagicMock()
        self.session = MagicMock()
        self.metric = Metric()
        self.metric.version_id = MagicMock(version_id=1)
        self.pylint_connector = PylintConnector(self.test_directory, self.version, self.session, self.config)

    def test_analyze_source_code_does_not_analyze_non_python_code(self):
        # Setup
        self.pylint_connector.config.language = 'java'
        logging_mock = Mock()

        # Action
        with patch('logging.error', logging_mock), self.assertRaises(Exception):
            self.pylint_connector.analyze_source_code()

        # Assert
        logging_mock.assert_any_call('PyLint is only used for Python language')

    def test_analyze_source_code_calls_compute_metrics_if_pylint_cbo_is_none(self):
        # Setup
        metric_mock = MagicMock(spec=Metric)
        metric_mock.pylint_cbo = None
        self.session.query.return_value.filter.return_value.first.return_value = metric_mock

        # Action
        with patch.object(self.pylint_connector, 'compute_metrics') as mock_cm:
            self.pylint_connector.analyze_source_code()

        # Assert
        mock_cm.assert_called_once()

    def test_analyse_source_code_analysis_already_done(self):
        # Setup
        logging_mock = Mock()
        metric_mock = MagicMock(spec=Metric)
        metric_mock.pylint_cbo = 10
        self.session.query.return_value.filter.return_value.first.return_value = metric_mock

        # Action
        with patch('logging.info', logging_mock):
            self.pylint_connector.analyze_source_code()

        # Assert
        logging_mock.assert_any_call('PyLint analysis already done for this version, version: ' + str(self.version.version_id))
    
