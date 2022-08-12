import logging
from models.issue import Issue
from models.version import Version
from models.commit import Commit
import lizard
from datetime import datetime
from sqlalchemy.sql import func

class LizardConnector:
    def __init__(self, directory, session, version_id):
        self.directory = directory
        self.session = session
        self.version_id = version_id

    def populate_db(self):
        """Populate the database from the GitHub API"""
        # Preserve the sequence below
        # self.create_commits_from_github()
        # self.create_issues_from_github()
        # self.create_versions_from_github()

    def analyze_source_code(self):
        """
        Recursivily analyse a folder containing source files
        """
        logging.info('analyze_source_code')

        i = lizard.analyze_file(f"{self.directory}/index.php")
        print(i.__dict__)

        # files = []
        # for issue in issues:
        #     bugs.append(
        #         Issue(
        #             project_id = self.project_id,
        #             title = issue.title,
        #             number = issue.number,
        #             created_at = issue.created_at
        #         )
        #     )
        # self.session.add_all(bugs)
        # self.session.commit()


