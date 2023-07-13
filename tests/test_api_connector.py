import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from connectors.survey import SurveyConnector

class SurveyConnectorTests(unittest.TestCase):
    def setUp(self):
        self.configuration = MagicMock()
        self.session = MagicMock()

        # Patch the 'requests' module in SurveyConnector
        patcher = mock.patch('connectors.survey.requests')
        self.mock_requests = patcher.start()

        self.connector = SurveyConnector(self.configuration, self.session)

    def test_get_all_comments(self):
        # Mock response data
        response_data = {
            "results": [
            {
                "id": 1, 
                "project_name": "project1",
                "user_id": "uuid1", 
                "timestamp": "timestamp1", 
                "feature_url": "url1", 
                "rating": "5",
                "comment": "First comment"
            },
            {
                "id": 2, 
                "project_name": "project2",
                "user_id": "uuid2", 
                "timestamp": "timestamp2", 
                "feature_url": "url2", 
                "rating": "4",
                "comment": "Second comment"
            },
        ],
            "page_size": 2
        }

        # Mock the send_request method to return the response data
        with patch.object(self.connector, "send_request", return_value=response_data):
            comments = self.connector.get_all_comments()

        # Assert the comments are retrieved correctly
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0]["id"], 1)
        self.assertEqual(comments[1]["id"], 2)

    def test_get_comments_by_project(self):
        # Mock response data
        response_data = {
            "results": [
            {
                "id": 1, 
                "project_name": "project1",
                "user_id": "uuid1", 
                "timestamp": "timestamp1", 
                "feature_url": "url1", 
                "rating": "5",
                "comment": "First comment"
            },
            {
                "id": 2, 
                "project_name": "project2",
                "user_id": "uuid2", 
                "timestamp": "timestamp2", 
                "feature_url": "url2", 
                "rating": "4",
                "comment": "Second comment"
            },
        ],
            "page_size": 2
        }

        # Mock the send_request method to return the response data
        with patch.object(self.connector, "send_request", return_value=response_data):
            comments = self.connector.get_comments_by_project("project1")

        # Assert the comments are retrieved correctly
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0]["id"], 1)
        self.assertEqual(comments[1]["id"], 2)

    def test_parse_comments_from_json(self):
        # Mock comments JSON data
        comments_json = [
            {
                "id": 1, 
                "project_name": "project1",
                "user_id": "uuid1", 
                "timestamp": "timestamp1", 
                "feature_url": "url1", 
                "rating": "5",
                "comment": "First comment"
            },
            {
                "id": 2, 
                "project_name": "project2",
                "user_id": "uuid2", 
                "timestamp": "timestamp2", 
                "feature_url": "url2", 
                "rating": "4",
                "comment": "Second comment"
            },
        ]

        # Parse comments from JSON
        comments = self.connector.parse_comments_from_json(comments_json, [])

        # Assert the comments are parsed correctly
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0].comment_id, 1)
        self.assertEqual(comments[1].comment_id, 2)

    def test_comment_exists(self):
        # Mock a Comment object
        comment = MagicMock()
        comment.comment_id = 1

        # Mock the query result in the session
        self.session.query().filter_by().first.return_value = comment

        # Check if the comment exists
        exists = self.connector.comment_exists(comment)

        # Assert that the comment exists
        self.assertTrue(exists)

    def test_comment_does_not_exist(self):
        # Mock a Comment object
        comment = MagicMock()
        comment.comment_id = 1

        # Mock the query result in the session
        self.session.query().filter_by().first.return_value = None

        # Check if the comment exists
        exists = self.connector.comment_exists(comment)

        # Assert that the comment does not exist
        self.assertFalse(exists)

if __name__ == "__main__":
    unittest.main()