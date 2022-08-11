import logging
from this import d
from models.issue import Issue
from models.project import Project
from models.version import Version
from models.commit import Commit
from github import Github
from datetime import datetime, date
from sqlalchemy.sql import func

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
                    title = issue.title,
                    number = issue.number,
                    created_at = issue.created_at
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
        git_commits = repo.get_commits()
        commits = []
        for git_commit in git_commits:
            commits.append(
                Commit(
                    project_id = self.project_id,
                    sha = git_commit.sha,
                    committer = git_commit.commit.committer.name,
                    date = git_commit.commit.committer.date,
                    additions = git_commit.stats.additions,
                    deletions = git_commit.stats.deletions,
                    total = git_commit.stats.total
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
        versions = []
        # GitHub API sorts the version from the latest to the oldest
        last_day = datetime.now()
        for release in releases:
            # Count the number of issues that occured between the start and end dates
            bugs_count = self.session.query(Issue).filter(Issue.created_at.between(release.published_at,last_day)).count()
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
                ).filter(Commit.date.between(release.published_at,last_day)).scalar()
            
            versions.append(
                Version(
                    project_id = self.project_id,
                    name = release.title,
                    start_date = release.published_at,
                    end_date = last_day,
                    bugs = bugs_count,
                    changes = rough_changes,
                    bug_velocity = bug_velo_release
                )
            )
            last_day = release.published_at

        self.session.add_all(versions)
        self.session.commit()

