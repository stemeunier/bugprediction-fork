import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models.database import setup_database
from sqlalchemy import desc
from dotenv import load_dotenv
import datetime
from models.version import Version
from models.commit import Commit
from models.issue import Issue
from github import Github

if __name__ == '__main__':
    load_dotenv()

    g = Github(os.environ["OTTM_GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["OTTM_SOURCE_REPO"])
    
    engine = db.create_engine(os.environ["OTTM_TARGET_DATABASE"])
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    # setup_database(engine)

    last_commit = session.query(Commit).order_by(desc(Commit.date)).limit(1).first()
    last_version = session.query(Version).order_by(desc(Version.start_date)).limit(1).first()
    last_issue = session.query(Issue).order_by(desc(Issue.created_at)).limit(1).first()

    git_commits = repo.get_commits(since=last_commit.date + datetime.timedelta(seconds=1))
    # releases = repo.get_releases(since=last_version.start_date)
    issues = repo.get_issues(since=last_issue.created_at + datetime.timedelta(seconds=1))

    for git_commit in git_commits:
        print(git_commit)

    for issue in issues:
        print(issue)