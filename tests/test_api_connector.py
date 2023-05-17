import json
import unittest
from unittest.mock import MagicMock, patch

from requests import Response
from connectors.survey import SurveyConnector
from models.comment import Comment


class TestSurveyConnector(unittest.TestCase):
    def setUp(self):
        self.config=MagicMock()
        self.config.survey_back_api_url="http://example"
        self.config.survey_project_name=''
        self.session = MagicMock()
        self.requestmock=MagicMock()
        self.responsemock=MagicMock(spec=Response)
        
        self.expected_comments ="""[
                {"id": 1, "project_name": "Project A", "user_id": 123, "timestamp": "2022-04-25 12:00:00",
                "feature_url": "https://example.com/features/1", "rating": 4, "comment": "Great feature!"},
                {"id": 2, "project_name": "Project A", "user_id": 456, "timestamp": "2022-04-25 13:00:00",
                "feature_url": "https://example.com/features/2", "rating": 3, "comment": "Needs improvement"},
                {"id": 3, "project_name": "Project B", "user_id": 789, "timestamp": "2022-04-25 14:00:00",
                "feature_url": "https://example.com/features/3", "rating": 5, "comment": "Awesome!"}
            ]"""
        self.responsemock.json.return_value=json.loads(self.expected_comments)
        self.responsemock._content=self.expected_comments
        self.requestmock.return_value=self.responsemock
        self.connector = SurveyConnector(self.config, self.session)

    def test_get_comments(self):
        with patch('requests.get', self.requestmock):
            expected_output=[
            Comment(
                comment_id=1,
                project_name='Project A',
                user_id=123,
                timestamp='2022-04-25 12:00:00',
                feature_url='https://example.com/features/1',
                rating=4,
                comment='Great feature!'
            ),
            Comment(
                comment_id=2,
                project_name='Project A',
                user_id=456,
                timestamp='2022-04-25 13:00:00',
                feature_url='https://example.com/features/2',
                rating=3,
                comment='Needs improvement'
            ),
            Comment(
                comment_id=3,
                project_name='Project B',
                user_id=789,
                timestamp='2022-04-25 14:00:00',
                feature_url='https://example.com/features/3',
                rating=5,
                comment='Awesome!'
            )
            ]
            
            comments = self.connector.get_comments()
            self.assertEqual(len(comments), len(expected_output))
            for i, comment in enumerate(comments):
                expected_out = expected_output[i]
                self.assertEqual(comment.comment_id, expected_out.comment_id)
                self.assertEqual(comment.project_name, expected_out.project_name)
                self.assertEqual(comment.user_id, expected_out.user_id)
                self.assertEqual(comment.timestamp, expected_out.timestamp)
                self.assertEqual(comment.feature_url, expected_out.feature_url)
                self.assertEqual(comment.rating, expected_out.rating)
                self.assertEqual(comment.comment, expected_out.comment)



if __name__ == '__main__':
    unittest.main()
