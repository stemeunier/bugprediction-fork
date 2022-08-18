import logging
import os

from sqlalchemy import desc
from unicodedata import name

import models
from models.issue import Issue
from models.version import Version
from models.commit import Commit
from models.author import Author
from models.alias import Alias
from github import Github
import datetime
from sqlalchemy.sql import func
import json
import pandas as pd


class GitHubConnector:
    """Connector to Github
    
    Attributes:
    -----------
     - token        Token for the GitHub API
     - repo         GitHub repository
     - session      Database connection managed by sqlachemy
     - project_id   Identifier of the project
    """

    def __init__(self, token, repo, session, project_id):
        self.token = token
        self.repo = repo
        self.session = session
        self.project_id = project_id

    def setup_aliases(self, aliases):
        """Populate the table of aliases if any alias if defined"""
        logging.info('setup_aliases')
        if aliases:
            aliases = y = json.loads(aliases)
            for alias, alternatives in aliases.items():
                author = self.session.query(Author).filter(Author.name == alias).first()
                if not author:
                    author = Author(name=alias)
                    self.session.add(author)
                    self.session.commit()
                for alternative in alternatives:
                    syno = self.session.query(Author).filter(Author.name == alternative).first()
                    if not syno:
                        syno = Author(name=alternative)
                        self.session.add(syno)
                        self.session.commit()
                    author_alias = self.session.query(Alias).filter(Alias.name == alternative).first()
                    if not author_alias:
                        author_alias = Alias(author_id=author.author_id, name=alternative)
                        self.session.add(author_alias)
                        self.session.commit()

    def populate_db(self):
        """Populate the database from the GitHub API"""
        # Preserve the sequence below
        self.create_commits_from_github()
        self.create_issues_from_github()
        self.create_versions_from_github()

    def create_issues_from_github(self):
        """
        Create issues into the database from GitHub Issues
        TODO: option to filter issues (take only issues considered as bug)
        """
        logging.info('create_issues_from_github')
        g = Github(self.token)
        repo = g.get_repo(self.repo)

        if self.session.query(Issue).all():
            last_issue = self.session.query(Issue).order_by(desc(models.issue.Issue.created_at)).get(1)
            git_issues = repo.get_issues(since=last_issue.created_at + datetime.timedelta(seconds=1), labels=['bug'])
        else:
            git_issues = repo.get_issues(labels=['bug'])  # Filter by labels=['bug']

        bugs = []
        for issue in git_issues:
            bugs.append(
                Issue(
                    project_id=self.project_id,
                    title=issue.title,
                    number=issue.number,
                    created_at=issue.created_at
                )
            )
        self.session.add_all(bugs)
        self.session.commit()

    def create_commits_from_github(self):
        """
        Create commits into the database from GitHub commits
        """
        logging.info('create_commits_from_github')
        g = Github(self.token)
        repo = g.get_repo(self.repo)

        if self.session.query(Commit).all():
            print("full")
            last_commit = self.session.query(Commit).order_by(desc(models.commit.Commit.date)).get(1)
            git_commits = repo.get_commits(since=last_commit.date + datetime.timedelta(seconds=1))
        else:
            print("empty")
            git_commits = repo.get_commits()

        commits = []
        for git_commit in git_commits:
            commits.append(
                Commit(
                    project_id=self.project_id,
                    sha=git_commit.sha,
                    committer=git_commit.commit.committer.name,
                    date=git_commit.commit.committer.date,
                    additions=git_commit.stats.additions,
                    deletions=git_commit.stats.deletions,
                    total=git_commit.stats.total
                )
            )
        self.session.add_all(commits)
        self.session.commit()

    def create_versions_from_github(self):
        """
        Create versions into the database from GitHub tags
        TODO must use release object
        """
        logging.info('create_versions_from_github')
        g = Github(self.token)
        repo = g.get_repo(self.repo)
        releases = repo.get_releases()
        last_version = self.session.query(Version).order_by(desc(models.version.Version.start_date)).get(1)
        if last_version:
            releases = [release for release in releases
                        if release.published_at > last_version.start_date or release.tag_name in os.environ["OTTM_INCLUDE_VERSIONS"]
                        and release.tag_name not in os.environ["OTTM_EXCLUDE_VERSIONS"]]
        else:
            releases = [release for release in releases if release.tag_name not in os.environ["OTTM_EXCLUDE_VERSIONS"]]

        versions = []
        # GitHub API sorts the version from the latest to the oldest
        last_day = datetime.datetime.now()
        for release in releases:
            # Count the number of issues that occurred between the start and end dates
            bugs_count = self.session.query(Issue).filter(
                Issue.created_at.between(release.published_at, last_day)).count()

            # Compute the bug velocity of the release
            delta = last_day - release.published_at
            days = delta.days
            if days > 0:
                bug_velo_release = bugs_count / days
            else:
                bug_velo_release = bugs_count

            # Compute a rough estimate of the total changes
            rough_changes = self.session.query(
                func.sum(Commit.total).label("total_changes")
            ).filter(Commit.date.between(release.published_at, last_day)).scalar()

            # Compute the average seniorship of the team
            team_members = self.session.query(Commit.committer).filter(
                Commit.date.between(release.published_at, last_day)
            ).group_by(Commit.committer).all()
            seniority_total = 0
            for member in team_members:
                first_commit = self.session.query(
                    func.min(Commit.date).label("date")
                ).filter(Commit.committer == member[0]).scalar()
                delta = last_day - first_commit
                seniority = delta.days
                seniority_total += seniority
            seniority_avg = seniority_total / max(len(team_members), 1)

            versions.append(
                Version(
                    project_id=self.project_id,
                    name=release.title,
                    tag=release.tag_name,
                    start_date=release.published_at,
                    end_date=last_day,
                    bugs=bugs_count,
                    changes=rough_changes,
                    avg_team_xp=seniority_avg,
                    bug_velocity=bug_velo_release
                )
            )
            last_day = release.published_at
        self.session.add_all(versions)
        self.session.commit()
