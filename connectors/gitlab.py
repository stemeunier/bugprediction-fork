import logging

from sqlalchemy import desc

from models.issue import Issue
from models.version import Version
from utils.timeit import timeit
from connectors.git import GitConnector
from gitlab import Gitlab
from datetime import datetime, timedelta

class GitLabConnector(GitConnector):
    """
    Connector to GitLab

    Attributes:
    -----------
     - base_url     URL to GitLab, empty if gitlab.com
    """
    def __init__(self, base_url, token, repo, session, project_id, directory):
        GitConnector.__init__(self, token, repo, session, project_id, directory)
        if not base_url and not self.token:
            logging.info("anonymous read-only access for public resources (GitLab.com)")
            self.api = Gitlab()
        if base_url and self.token:
            logging.info("private token or personal token authentication (self-hosted GitLab instance)")
            self.api = Gitlab(url=base_url, private_token=self.token)
        if not base_url and self.token:
            logging.info("private token or personal token authentication (GitLab.com)")
            self.api = Gitlab(private_token=self.token)
        
        # Check the authentification
        self.api.auth()

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
        last_issue = self.session.query(Issue).order_by(desc(Issue.updated_at)).get(1)
        if last_issue is not None:
            # Update existing database by fetching new issues
            if not self.configuration.issue_tags:
                git_issues = self.remote.issues.list(state="all", created_after=last_issue.updated_at + timedelta(seconds=1))
            else:
                git_issues = self.remote.issues.list(state="all", created_after=last_issue.updated_at + timedelta(seconds=1),
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
            if issue.author['username'] not in self.configuration.exclude_issuers:
                bugs.append(
                    Issue(
                        project_id=self.project_id,
                        title=issue.title,
                        number=issue.iid,
                        created_at=datetime.strptime(issue.created_at, '%Y-%m-%dT%H:%M:%S.%f%z'),
                        updated_at=datetime.strptime(issue.updated_at, '%Y-%m-%dT%H:%M:%S.%f%z')
                    )
                )

        # Remove potential duplicated values
        # list(dict.fromkeys(bugs))
        self.session.add_all(bugs)
        self.session.commit()
    
    @timeit
    def create_versions_from_gitlab(self):
        """
        Create versions into the database from GitLab releases
        """
        logging.info('create_versions_from_gitlab')
        releases = self.remote.releases.list()
        self.session.query(Version).delete()
        self.session.commit()

        versions = []
        # GitLab API sorts the version from the latest to the oldest
        last_day = datetime.now()
        for release in releases:
            versions.append(
                Version(
                    project_id=self.project_id,
                    name=release.name,
                    tag=release.tag_name,
                    start_date=datetime.strptime(release.released_at, '%Y-%m-%dT%H:%M:%S.%f%z'),
                    end_date=last_day
                )
            )
            last_day = datetime.strptime(release.released_at, '%Y-%m-%dT%H:%M:%S.%f%z')
        
        self.session.add_all(versions)
        self.session.commit()
