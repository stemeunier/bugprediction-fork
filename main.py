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
    # git.populate_db()

    # Checkout, execute the tool and inject CSV result into the database
    #with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_dir = tempfile.mkdtemp()
    logging.info('created temporary directory: ' + tmp_dir)
    
    # Clone the repository
    process = subprocess.run(["git", "clone", os.environ["OTTM_SOURCE_REPO_URL"]], 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        cwd=tmp_dir)
    logging.info('Executed command line: ' + ' '.join(process.args))
    repo_dir = os.path.join(tmp_dir, os.environ["OTTM_SOURCE_PROJECT"])

    # List the versions and checkout each one of them
    versions = session.query(Version).all()
    for version in versions:
        process = subprocess.run(["git", "checkout", version.tag], 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        cwd=repo_dir)
        logging.info('Executed command line: ' + ' '.join(process.args))
        
        # Generate the git log for the version
        print(version.start_date.isoformat())
        print(version.end_date.isoformat())
        fd, git_log_file = tempfile.mkstemp(suffix=".log")
        fh = os.fdopen(fd, "w")
        logging.info('Generate GIT log file: ' + git_log_file)
        # git log --all --numstat --date=short --pretty=format:'--%h--%ad--%aN' --no-renames --since '2014-04-09T21:16:07' --until '2014-05-22T17:52:09'  > gitlogfile.log
        process = subprocess.run(["git", "--no-pager", "log", "--all", "--numstat", "--date=short", '--pretty=format:"--%h--%ad--%aN"', "--no-renames",
                        "--since='" + version.start_date.isoformat() + "'",
                        "--until='" + version.start_date.isoformat() + "'"],
                        stdout=fh,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        cwd=repo_dir)
        logging.info('Executed command line: ' + ' '.join(process.args))

        # Get statistics with lizard
        lizard = LizardConnector(directory=repo_dir, session=session, version_id=version.version_id)
        lizard.analyze_source_code()

