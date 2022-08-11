import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
import platform
import subprocess
from models.project import Project
from models.issue import Issue
from models.database import setup_database
from dotenv import load_dotenv
from githubconnector import GitHubConnector

def check_output(command):
    return subprocess.check_output(command, shell = True).decode("utf-8")

def get_issues_from_github():
    token = os.environ["OTTM_GITHUB_TOKEN"]
    g = Github(token)
    repo = g.get_repo("microsoft/vscode")
    issues = repo.get_issues()  # Filter by labels=['bug']
    return issues

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    logging.info('python: ' + platform.python_version())
    logging.info('system: ' + platform.system())
    logging.info('machine: ' + platform.machine())
    #logging.info('java: ' + check_output("java -version"))
    
    engine = db.create_engine(os.environ["OTTM_TARGET_DATABASE"])
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    setup_database(engine)
    
    project = Project(name="Project", repo="any", language="Java")
    session.add(project)
    session.commit()
    
    git = GitHubConnector(
        os.environ["OTTM_GITHUB_TOKEN"],
        "bbalet/jorani",
        session,
        project.project_id)

    # TODO : wrap the calls below in a method as we must follow the order
    git.create_commits_from_github()
    git.create_issues_from_github()
    git.create_versions_from_github()

    # TODO Iteration Example to be deleted
    issues = session.query(Issue).all()
    for row in issues:
        print(f"Issue: {row.title}")
    # DELETE ME