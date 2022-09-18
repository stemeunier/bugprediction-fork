import logging

from sqlalchemy import desc
from unicodedata import name

import models
from models.issue import Issue
from models.version import Version
from models.commit import Commit
from github import Github
import datetime
from sqlalchemy.sql import func
from gitconnector import GitConnector
from utils.timeit import timeit

class GitHubConnector(GitConnector):
    """
    Connector to Github
    """

    def __init__(self, token, repo, session, project_id, directory):
        GitConnector.__init__(self, token, repo, session, project_id, directory)
        self.api = Github(self.token)
        self.remote = self.api.get_repo(self.repo)

    def populate_db(self):
        """Populate the database from the GitHub API"""
        # Preserve the sequence below
        self.create_versions_from_github()
        self.create_commits_from_repo()
        self.create_issues_from_github()

    @timeit
    def create_issues_from_github(self):
        """
        Create issues into the database from GitHub Issues
        """
        logging.info('create_issues_from_github')

        # Check if a database already exist
        last_issue = self.session.query(Issue).order_by(desc(models.issue.Issue.updated_at)).get(1)
        if last_issue is not None:
            # Update existing database by fetching new issues
            if not self.configuration.issue_tags:
                git_issues = self.remote.get_issues(state="all", since=last_issue.updated_at + datetime.timedelta(seconds=1))
            else:
                git_issues = self.remote.get_issues(state="all", since=last_issue.updated_at + datetime.timedelta(seconds=1),
                                            labels=self.configuration.issue_tags)  # e.g. Filter by labels=['bug']
        else:
            # Create a database with all issues
            if not self.configuration.issue_tags:
                git_issues = self.remote.get_issues(state="all")
            else:
                git_issues = self.remote.get_issues(state="all", labels=self.configuration.issue_tags)  # e.g. Filter by labels=['bug']

        # versions = self.session.query(Version).all()
        logging.info('Syncing ' + str(git_issues.totalCount) + ' issue(s) from GitHub')

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
    def create_versions_from_github(self):
        """
        Create versions into the database from GitHub tags
        """
        logging.info('create_versions_from_github')
        releases = self.remote.get_releases()
        self.session.query(Version).delete()
        self.session.commit()

        # Check if a database already exist
        # last_version = self.session.query(Version).order_by(desc(Version.start_date)).get(1)
        # if last_version:
        #     # Update existing database by fetching new versions and versions on "include" list but not in "exclude" one
        #     # TODO : Not working with the last_day algo
        #     releases = [release for release in releases
        #                 if (release.published_at > last_version.start_date + datetime.timedelta(seconds=1)
        #                     or release.tag_name in self.configuration.include_versions)
        #                 and release.tag_name not in self.configuration.exclude_versions]

        # else:
            # Create a database with all versions
            # releases = [release for release in releases if release.tag_name not in self.configuration.exclude_versions]

        # Remove potential duplicated values
        # list(dict.fromkeys(releases))
        # commits = self.session.query(Commit).all()
        # issues = self.session.query(Issue).all()
        # versions = self.session.query(Version).all()

        # for version in versions:
        #     for commit in commits:
        #         if version.end_date > commit.date > version.start_date:
        #             self.session.delete(commit)
        #     for issue in issues:
        #         if version.end_date > issue.created_at > version.start_date:
        #             self.session.delete(issue)
        #     if version.tag in self.configuration.exclude_versions:
        #         self.session.delete(version)


        versions = []
        # GitHub API sorts the version from the latest to the oldest
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
