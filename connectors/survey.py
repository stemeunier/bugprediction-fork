import logging
import requests

from models.comment import Comment

class SurveyConnector:
    def __init__(self, configuration, session):
        self.configuration=configuration
        self.session=session

    def populate_comments(self):
        comments=self.get_comments()
        self.save_comments_to_db(comments)

    def get_comments(self):
        comments_list=[]
        if len(self.configuration.survey_project_name) == 0:
            response = requests.get(f"{self.configuration.survey_back_api_url}/comments")
            response.raise_for_status()
            comments_json = response.json()
            comments_list.append(comments_json)
        else:
            for project_name in self.configuration.survey_project_name:
                response = requests.get(f"{self.configuration.survey_back_api_url}/comments?project_name={project_name}")
                response.raise_for_status()
                comments_list.append(response.json())
        merged_comments_list = [comment for sublist in comments_list for comment in sublist]
        comments = self.parse_comments_from_json(merged_comments_list, self.configuration.survey_project_name)
        
        return comments


    def parse_comments_from_json(self,comments_json, project_names):
        comments = []
        for comment_json in comments_json:
            
            comment = Comment(
                comment_id=comment_json['id'],
                project_name=comment_json['project_name'],
                user_id=comment_json['user_id'],
                timestamp=comment_json['timestamp'],
                feature_url=comment_json['feature_url'],
                rating=comment_json['rating'],
                comment=comment_json['comment']
            )

            if not project_names or comment.project_name in project_names:
                comments.append(comment)
        
        return comments
    
    def save_comments_to_db(self, comments):
        try:
            for comment in comments:
            # Check if comment already exists in the database
                if not self.session.query(Comment).filter_by(comment_id=comment.comment_id).first():
                    self.session.add(comment)
            self.session.commit()
            logging.info("Comments added to database")
        except Exception as e:
            logging.error("An error occurred while saving Comments")
            logging.error(str(e))