from abc import ABC, abstractmethod
import logging
import datetime
import json

from pydriller import Repository
from sqlalchemy.sql import func
from sqlalchemy import desc

from configuration import Configuration
from models.version import Version
from models.commit import Commit
from models.issue import Issue
from models.metric import Metric
from models.author import Author
from models.alias import Alias
from utils.timeit import timeit

class GitConnector(ABC):
    """Connector to Github
    
    Attributes:
    -----------
     - token        Token for the SCM API
     - repo         Git repository (cloned locally, not bare repo)
     - current      Branch containing the next release (e.g. "devel")
     - session      Database connection managed by sqlachemy
     - project_id   Identifier of the project
     - directory    Folder (temporary) where the project is cloned
    """

    def __init__(self, token, repo, current, session, project_id, directory):
        self.token = token
        self.repo = repo
        self.current = current
        self.session = session
        self.project_id = project_id
        self.directory = directory
        self.configuration = Configuration()

    @timeit
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

    @timeit
    def create_commits_from_repo(self):
        """
        Create commits into the database from GitHub commits
        Commits are not linked to version
        """
        logging.info('create_commits_from_repo')

        # Check what was the las inserted commit
        last_commit = self.session.query(Commit).order_by(Commit.date.desc()).first()
        if last_commit is not None:
            last_synced = last_commit.date + datetime.timedelta(seconds=1)
            logging.info('Update existing database by fetching new commits since ' + str(last_synced))
            git_commits = Repository(self.directory, since=last_synced, only_no_merge=True).traverse_commits()
        else:
            logging.info('Create a database with all commits')
            git_commits = Repository(self.directory, only_no_merge=True).traverse_commits()

        commits = []
        for git_commit in git_commits:
            if git_commit.committer.name not in self.configuration.exclude_authors:
                commits.append(
                    Commit(
                        project_id=self.project_id,
                        hash=git_commit.hash,
                        committer=git_commit.committer.name,
                        date=git_commit.committer_date,
                        insertions=git_commit.insertions,
                        deletions=git_commit.deletions,
                        lines=git_commit.lines,
                        files=git_commit.files,
                        dmm_unit_size=git_commit.dmm_unit_size,
                        dmm_unit_complexity=git_commit.dmm_unit_complexity,
                        dmm_unit_interfacing=git_commit.dmm_unit_interfacing
                    )
                )
            
        self.session.add_all(commits)
        self.session.commit()

    @timeit
    def compute_version_metrics(self):
        """Compute version related metics:
        - Rough volume of changes (total lines)
        - Number of issues
        - Bug velocity
        - Average seniorship of the team
        """
        versions = self.session.query(Version).all()

        for version in versions:
            # Exclude current branch as it is the next release on which we want to predict the number of bugs
            if version.tag.lower() != self.current.lower():
                # Count the number of issues that occurred between the start and end dates
                bugs_count = self.session.query(Issue).filter(
                    Issue.created_at.between(version.start_date, version.end_date)).count()

                # Compute the bug velocity of the release
                delta = version.end_date - version.start_date
                days = delta.days
                if days > 0:
                    bug_velo_release = bugs_count / days
                else:
                    bug_velo_release = bugs_count

                # Compute a rough estimate of the total changes
                rough_changes = self.session.query(
                    func.sum(Commit.lines).label("total_changes")
                ).filter(Commit.date.between(version.start_date, version.end_date)).scalar()

                # Compute the average seniorship of the team
                team_members = self.session.query(Commit.committer).filter(
                    Commit.date.between(version.start_date, version.end_date)
                ).group_by(Commit.committer).all()
                seniority_total = 0
                for member in team_members:
                    first_commit = self.session.query(
                        func.min(Commit.date).label("date")
                    ).filter(Commit.committer == member[0]).scalar()
                    delta = version.end_date - first_commit
                    seniority = delta.days
                    seniority_total += seniority
                seniority_avg = seniority_total / max(len(team_members), 1)

                version.bugs=bugs_count
                version.changes=rough_changes
                version.avg_team_xp=seniority_avg
                version.bug_velocity=bug_velo_release
                self.session.commit()
            
    def clean_next_release_metrics(self):
        """
        Clean the metrics assosciated to the current branch so as to compute them again
        """
        next_release = self.session.query(Version).filter(Version.name == "Next Release").first()
        self.session.query(Metric).filter(Metric.version_id == next_release.version_id).delete()
        self.session.commit()
        logging.info("Deleted Metrics associated with version " + next_release.name)

    def populate_db(self):
        """Populate the database from the Git API"""
        # Preserve the sequence below
        self.clean_next_release_metrics()
        self.create_versions()
        self.create_commits_from_repo()
        self.create_issues()
        self.compute_version_metrics()

    @abstractmethod
    def create_issues(self):
        raise NotImplementedError

    @abstractmethod
    def create_versions(self):
        raise NotImplementedError