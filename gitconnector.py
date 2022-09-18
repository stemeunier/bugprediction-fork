import logging
import datetime
import json

from pydriller import Repository
from sqlalchemy.sql import func
from sqlalchemy import desc

from configuration import Configuration
from models.version import Version
from models.commit import Commit
from models.author import Author
from models.alias import Alias
from utils.timeit import timeit

class GitConnector:
    """Connector to Github
    
    Attributes:
    -----------
     - token        Token for the GitHub API
     - repo         Git repository (cloned locally, not bare repo)
     - session      Database connection managed by sqlachemy
     - project_id   Identifier of the project
    """

    def __init__(self, token, repo, session, project_id, directory):
        self.token = token
        self.repo = repo
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
