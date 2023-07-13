import logging
import requests

from models.comment import Comment

class SurveyConnector:
    """
    Connector class for retrieving survey comments and storing them in a database.
    """

    def __init__(self, configuration, session):
        """
        Initialize a new SurveyConnector instance.

        Args:
            configuration: The survey configuration object.
            session: The database session object.
        """
        self.configuration = configuration
        self.session = session

        self.verify_connection()

    def populate_comments(self):
        """
        Retrieve comments and save them to the database.
        """
        if self.configuration.survey_back_api_url != "":
            comments = self.get_comments()
            self.save_comments_to_db(comments)

    def get_comments(self):
        """
        Retrieve comments based on the survey project configuration.

        Returns:
            List of Comment objects.
        """
        comments_list = []
        if len(self.configuration.survey_project_name) == 0:
            comments_list = self.get_all_comments()
        else:
            for project_name in self.configuration.survey_project_name:
                comments_list.extend(self.get_comments_by_project(project_name))
        
        return self.parse_comments_from_json(comments_list, self.configuration.survey_project_name)

    def get_all_comments(self):
        """
        Retrieve all comments from the survey API.

        Returns:
            List of Comment objects.
        """
        comments_list = []
        url = f"{self.configuration.survey_back_api_url}/comments"
        page = 1
        response = self.send_request(url, page=page)

        while response and page < response["page_size"]:
            comments_list.extend(response["results"])
            page += 1
            response = self.send_request(url, page=page)
        
        return comments_list

    def get_comments_by_project(self, project_name):
        """
        Retrieve comments for a specific project from the survey API.

        Args:
            project_name: Name of the project.

        Returns:
            List of Comment objects.
        """
        comments_list = []
        url = f"{self.configuration.survey_back_api_url}/comments?project_name={project_name}"
        page = 1
        response = self.send_request(url, page=page)

        while response and page < response["page_size"]:
            comments_list.extend(response["results"])
            page += 1
            response = self.send_request(url, page=page)
        
        return comments_list

    def send_request(self, url, page=1):
        """
        Send an HTTP GET request to the specified URL.

        Args:
            url: The URL to send the request to.
            page: The page number for pagination (default: 1).

        Returns:
            The JSON response as a dictionary, or None if the request fails.
        """
        try:
            separator = '&' if '?' in url else '?'
            response = requests.get(f"{url}{separator}page={page}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred while sending a request to {url}: {str(e)}")
            return None

    def parse_comments_from_json(self, comments_json, project_names):
        """
        Parse comments from JSON into Comment objects.

        Args:
            comments_json: The JSON representation of comments.
            project_names: List of project names to filter comments (optional).

        Returns:
            List of Comment objects.
        """
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
        """
        Save comments to the database.

        Args:
            comments: List of Comment objects.
        """
        try:
            for comment in comments:
                if not self.comment_exists(comment):
                    self.session.add(comment)
            self.session.commit()
            logging.info("Survey: Comments added to database")
        except Exception as e:
            logging.error("Survey: An error occurred while saving comments")
            logging.error(str(e))

    def comment_exists(self, comment):
        """
        Check if a comment already exists in the database.

        Args:
            comment: The Comment object to check.

        Returns:
            True if the comment exists, False otherwise.
        """
        return self.session.query(Comment).filter_by(comment_id=comment.comment_id).first() is not None

    def verify_connection(self):
        try:
            response = requests.head(f"{self.configuration.survey_back_api_url}/comments")
            response.raise_for_status()
        except requests.HTTPError as e:
            # This error occurs when the method is not allowed for the called route
            # It means the server is reachable
            # So we don't raise the status error
            if e.response.status_code != 405:
                raise e
        except requests.ConnectionError:
            logging.error("Survey API is unreachable.")
            raise ConnectionError("Survey API is unreachable.")
