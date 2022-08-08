import logging
from models.issue import Issue
from models.project import Project
from models.version import Version
from github import Github

class GitHubConnector:
    def __init__(self, token, repo, session, project_id):
        self.token = token
        self.repo = repo
        self.session = session
        self.project_id = project_id

    def create_issues_from_github(self):
        """
        Create issues into the database from GitHub Issues
        TODO: option to filter issues (take only issues considered as bug)
        """
        logging.info('create_issues_from_github')
        g = Github(self.token)
        repo = g.get_repo(self.repo)
        issues = repo.get_issues()  # Filter by labels=['bug']
        bugs = []
        for issue in issues:
            bugs.append(
                Issue(
                    project_id = self.project_id,
                    title=issue.title,
                    number=issue.number,
                    created_at=issue.created_at
                )
            )
        self.session.add_all(bugs)
        self.session.commit()

    def create_versions_from_github(self):
        """
        Create versions into the database from GitHub tags
        TODO: must use release object
        """
        logging.info('create_versions_from_github')
        g = Github(self.token)
        repo = g.get_repo(self.repo)
        tags = repo.get_tags()
        versions = []
        for tag in tags:
            versions.append(
                Version(
                    project_id = self.project_id,
                    name=""
                )
            )
        self.session.add_all(versions)
        self.session.commit()


    
