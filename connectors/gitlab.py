import logging
from time import sleep
import gitlab

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
    def __init__(self, project_id, directory, base_url, token, repo, current, session, config):
        GitConnector.__init__(self, project_id, directory, token, repo, current, session, config)
        if not base_url and not self.token:
            logging.info("anonymous read-only access for public resources (GitLab.com)")
            self.api = Gitlab()
        if base_url and self.token:
            logging.info("private token or personal token authentication (self-hosted GitLab instance)")
            self.api = Gitlab(url=base_url, private_token=self.token)
        if not base_url and self.token:
            logging.info("private token or personal token authentication (GitLab.com)")
            self.api = Gitlab(private_token=self.token)
        
        # Check the authentification. Doesn't work for public read only access
        if base_url or self.token:
            self.api.auth()

        self.remote = self.api.projects.get(self.repo)

    def _get_issues(self, since=None, labels=None):
        if not since:
            since = None
        if not labels:
            labels = None

        try:
            return self.remote.issues.list(state="all", created_after=since, with_labels_details=labels)
        except gitlab.GitlabJobRetryError:
            sleep(self.configuration.retry_delay)
            self._get_issues(since, labels)
    
    def _get_releases(self, all, order_by, sort):
        if not all:
            all = None
        if not order_by:
            order_by = None
        if not sort:
            sort = None
            
        try:
            return self.remote.releases.list(all=all, order_by=order_by,sort=sort)
        except gitlab.GitlabJobRetryError:
            sleep(self.configuration.retry_delay)
            self._get_releases(all, order_by, sort)
        
    @timeit
    def create_issues(self):
        """
        Create issues into the database from GitLab Issues
        """
        logging.info('GitLabConnector: create_issues')

        # Check if a database already exist
        last_issue = self.session.query(Issue) \
                         .filter(Issue.project_id == self.project_id) \
                         .order_by(desc(Issue.updated_at)).first()
        if last_issue is not None:
            # Update existing database by fetching new issues
            if not self.configuration.issue_tags:
                git_issues = self._get_issues(since=last_issue.updated_at + timedelta(seconds=1))
            else:
                git_issues = self._get_issues(since=last_issue.updated_at + timedelta(seconds=1),
                                                    with_labels_details=self.configuration.issue_tags)  # e.g. Filter by labels=['bug']
        else:
            # Create a database with all issues
            if not self.configuration.issue_tags:
                git_issues = self._get_issues()
            else:
                git_issues = self._get_issues(labels=self.configuration.issue_tags)    # e.g. Filter by labels=['bug']
        
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
    def create_versions(self):
        """
        Create versions into the database from GitLab releases
        """
        logging.info('GitLabConnector: create_versions')
        releases = self._get_releases(all=True, order_by="released_at", sort="asc")
        self._clean_project_existing_versions()

        versions = []
        previous_release_published_at = self._get_first_commit_date()

        for release in releases:
            release_published_at = datetime.strptime(release.released_at, '%Y-%m-%dT%H:%M:%S.%f%z')
            versions.append(
                Version(
                    project_id=self.project_id,
                    name=release.name,
                    tag=release.tag_name,
                    start_date=previous_release_published_at,
                    end_date=release_published_at,
                )
            )
            previous_release_published_at = release_published_at

        # Put current branch at the end of the list
        versions.append(
            Version(
                project_id=self.project_id,
                name=self.configuration.next_version_name,
                tag=self.current,
                start_date=previous_release_published_at,
                end_date=datetime.now(),
            )
        )
        self.session.add_all(versions)
        self.session.commit()
