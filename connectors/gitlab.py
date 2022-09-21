import logging

from sqlalchemy import desc

import models
from models.issue import Issue
from models.version import Version
from utils.timeit import timeit
from connectors.git import GitConnector
from gitlab import Gitlab
import datetime

class GitLabConnector(GitConnector):
    """
    Connector to GitLab
    """
    def __init__(self, token, repo, session, project_id, directory):
        GitConnector.__init__(self, token, repo, session, project_id, directory)
        self.api = Gitlab("https://gitlab.com", private_token=self.token)
        self.remote = self.api.projects.get(self.repo)
        
    def populate_db(self):
        """Populate the database from the GitLab API"""
        # Preserve the sequence below
        self.create_versions_from_gitlab()
        self.create_commits_from_repo()
        self.create_issues_from_gitlab()
    
    @timeit
    def create_issues_from_gitlab(self):
        """
        Create issues into the database from GitLab Issues
        """
        logging.info('create_issues_from_gitlab')

        # Check if a database already exist
        last_issue = self.session.query(Issue).order_by(desc(models.issue.Issue.updated_at)).get(1)
        if last_issue is not None:
            # Update existing database by fetching new issues
            if not self.configuration.issue_tags:
                git_issues = self.remote.issues.list(state="all", created_after=last_issue.updated_at + datetime.timedelta(seconds=1))
            else:
                git_issues = self.remote.issues.list(state="all", created_after=last_issue.updated_at + datetime.timedelta(seconds=1),
                                                    with_labels_details=self.configuration.issue_tags)  # e.g. Filter by labels=['bug']
        else:
            # Create a database with all issues
            if not self.configuration.issue_tags:
                git_issues = self.remote.issues.list(state="all")
            else:
                git_issues = self.remote.issues.list(state="all", with_labels_details=self.configuration.issue_tags)    # e.g. Filter by labels=['bug']
        
        # versions = self.session.query(Version).all
        logging.info('Syncing ' + str(len(git_issues)) + ' issue(s) from GitLab')

        bugs = []
        # for version in versions:
        for issue in git_issues:
            # Check if the issue is linked to a selected version (included or not excluded)
            # if version.end_date > issue.created_at > version.start_date:
            if issue.user.login not in self.configuration.exclude_issuers:
                bugs.append(
                    Issue(
                        project_id=self.project_id,
                        title=issue.title,
                        number=issue.number,
                        created_at=issue.created_at,
                        updated_at=issue.updated_at
                    )
                )

        # Remove potential duplicated values
        # list(dict.fromkeys(bugs))
        self.session.add_all(bugs)
        self.session.commit()
    
    @timeit
    def create_versions_from_gitlab(self):
        """
        Create versions into the database from GitLab tags
        """
        logging.info('create_versions_from_gitlab')
        releases = self.remote.releases.list()
        self.session.query(Version).delete()
        self.session.commit()

        print(releases)

        versions = []
        # GitLab API sorts the version from the latest to the oldest
        last_day = datetime.datetime.now()
        for release in releases:
            versions.append(
                Version(
                    project_id=self.project_id,
                    name=release.title,
                    tag=release.tag_name,
                    start_date=release.published_at,
                    end_date=last_day
                )
            )
            last_day = release.published_at
        
        self.session.add_all(versions)
        self.session.commit()