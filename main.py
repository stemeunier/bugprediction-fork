import os
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
import platform
import subprocess
import tempfile

from ckconnector import CkConnector
from jpeekconnector import JPeekConnector
from models.project import Project
from models.version import Version
from models.database import setup_database
from dotenv import load_dotenv
from githubconnector import GitHubConnector
from codemaatconnector import CodeMaatConnector
from fileanalyzer import FileAnalyzer
from metrics.versions import compute_version_metrics

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    logging.info('python: ' + platform.python_version())
    logging.info('system: ' + platform.system())
    logging.info('machine: ' + platform.machine())
    # logging.info('java: ' + check_output("java -version"))

    engine = db.create_engine(os.environ["OTTM_TARGET_DATABASE"])
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    setup_database(engine)

    project = session.query(Project).filter(Project.name == os.environ["OTTM_SOURCE_PROJECT"]).first()
    if not project:
        project = Project(name=os.environ["OTTM_SOURCE_PROJECT"],
                        repo=os.environ["OTTM_SOURCE_REPO"],
                        language=os.environ["OTTM_LANGUAGE"])
        session.add(project)
        session.commit()

    # Checkout, execute the tool and inject CSV result into the database
    # with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_dir = tempfile.mkdtemp()
    logging.info('created temporary directory: ' + tmp_dir)

    # Clone the repository
    process = subprocess.run(["git", "clone", os.environ["OTTM_SOURCE_REPO_URL"]],
                             stdout=subprocess.PIPE,
                             cwd=tmp_dir)
    logging.info('Executed command line: ' + ' '.join(process.args))
    repo_dir = os.path.join(tmp_dir, os.environ["OTTM_SOURCE_PROJECT"])

    # Populate the database
    git = GitHubConnector(
        os.environ["OTTM_GITHUB_TOKEN"],
        os.environ["OTTM_SOURCE_REPO"],
        session,
        project.project_id,
        repo_dir)
    git.populate_db()
    git.setup_aliases(os.environ["OTTM_AUTHOR_ALIAS"])
    compute_version_metrics(session)

    # List the versions and checkout each one of them
    versions = session.query(Version).all()
    for version in versions:
        process = subprocess.run(["git", "checkout", version.tag],
                                 stdout=subprocess.PIPE,
                                 cwd=repo_dir)
        logging.info('Executed command line: ' + ' '.join(process.args))

        # Get statistics from git log with codemaat
        # codemaat = CodeMaatConnector(repo_dir, session, version)
        # codemaat.analyze_git_log()

        # Get metrics with CK
        ck = CkConnector(directory=repo_dir, session=session, version=version)
        ck.analyze_source_code()

        # Get statistics with lizard
        lizard = FileAnalyzer(directory=repo_dir, session=session, version=version)
        lizard.analyze_source_code()

        # Get metrics with JPeek
        jp = JPeekConnector(directory=repo_dir, session=session, version=version)
        jp.analyze_source_code()
