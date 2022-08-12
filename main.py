import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
import platform
import subprocess
import tempfile
from models.project import Project
from models.version import Version
from models.database import setup_database
from dotenv import load_dotenv
from githubconnector import GitHubConnector
from lizardconnector import LizardConnector

def check_output(command):
    return subprocess.check_output(command, shell = True).decode("utf-8")

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
    
    project = Project(name=os.environ["OTTM_SOURCE_PROJECT"],
                     repo=os.environ["OTTM_SOURCE_REPO"],
                     language=os.environ["OTTM_LANGUAGE"])
    session.add(project)
    session.commit()
    
    # Populate the database
    git = GitHubConnector(
        os.environ["OTTM_GITHUB_TOKEN"],
        os.environ["OTTM_SOURCE_REPO"],
        session,
        project.project_id)
    git.populate_db()



