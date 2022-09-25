import os
import sys
import logging
import platform
import subprocess
import tempfile

import click
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from exporters.html import HtmlExporter

from models.project import Project
from models.version import Version
from models.issue import Issue
from models.metric import Metric
from models.model import Model
from models.database import setup_database
from connectors.ck import CkConnector
from connectors.jpeek import JPeekConnector
from connectors.github import GitHubConnector
from connectors.gitlab import GitLabConnector
from connectors.codemaat import CodeMaatConnector
from connectors.fileanalyzer import FileAnalyzer
from exporters import flatfile
from ml.bugvelocity import BugVelocity

session = None
project = None

@click.group()
@click.pass_context
def cli(ctx):
    """Datamining on git repository to predict the risk of releasing next version"""
    pass

@cli.command()
@click.option('--output', default='.', help='Destination folder', envvar="OTTM_OUTPUT_FOLDER")
@click.option('--format', default='csv', help='Output format (csv,parquet)', envvar="OTTM_OUTPUT_FORMAT")
@click.pass_context
def export(ctx, output, format):
    """Export the database to a flat format"""
    logging.info("export")
    if output is None:
        logging.error("Parameter output is mandatory")
        sys.exit('Parameter output is mandatory')
    if format is None:
        logging.error("Parameter format is mandatory")
        sys.exit('Parameter format is mandatory')
    else:
        format = format.lower()
        if format not in ['csv','parquet']:
            logging.error("Unsupported output format")
            sys.exit('Unsupported output format')
    exporter = flatfile.FlatFileExporter(session, output)
    if format == 'csv':
        exporter.export_to_csv("metrics.csv")
    elif format == 'parquet':
        exporter.export_to_parquet("metrics.parquet")

@cli.command()
@click.option('--output', default='.', help='Destination folder')
@click.pass_context
def report(ctx, output):
    """Create a basic HTML report"""
    exporter = HtmlExporter(session, output)
    exporter.generate(project, 'report.html')
    pass

@cli.command()
@click.option('--model-name', default='bugvelocity', help='Name of the model')
@click.pass_context
def train(ctx, model_name):
    """Train a model"""
    # TODO : the concrete object should be returned by a factory
    model = BugVelocity(session, project.project_id)
    model.train()
    click.echo("Model was trained")

@cli.command()
@click.option('--model-name', default='bugvelocity', help='Name of the model')
@click.pass_context
def predict(ctx, model_name):
    """Predict next value with a trained model"""
    # TODO : the concrete object should be returned by a factory
    model = BugVelocity(session, project.project_id)
    value = model.predict()
    click.echo("Predicted value : " + str(value))

@cli.command()
@click.pass_context
def info(ctx):
    """Provide information about the current configuration
    If these values are not populated, the tool won't work.
    """
    versions_count = session.query(Version).filter(Version.project_id == project.project_id).count()
    issues_count = session.query(Issue).filter(Issue.project_id == project.project_id).count()
    metrics_count = session.query(Metric).join(Version).filter(Version.project_id == project.project_id).count()
    trained_models = session.query(Model.name).filter(Version.project_id == project.project_id).all()

    out = """ -- OTTM Bug Predictor --
    Project  : {project}
    Language : {language}
    SCM      : {scm} / {repo}
    Release  : {release}
    
    Versions : {versions}
    Issues   : {issues}
    Metrics  : {metrics}

    Trained models : {models}
    """.format(
        project=os.environ["OTTM_SOURCE_PROJECT"],
        language=os.environ["OTTM_LANGUAGE"],
        scm=os.environ["OTTM_SOURCE_REPO_SMC"],
        repo=os.environ["OTTM_SOURCE_REPO_URL"],
        release=os.environ["OTTM_CURRENT_BRANCH"],
        versions=versions_count,
        issues=issues_count,
        metrics=metrics_count,
        models=",".join(trained_models[0])
        )
    click.echo(out)

@cli.command()
@click.pass_context
def check(ctx):
    """Check the consistency of the configuration and perform basic tests"""
    pass

@cli.command()
@click.pass_context
def populate(ctx):
    """Populate the database with the provided configuration"""

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
    if os.environ["OTTM_SOURCE_REPO_SMC"] == "github":
        logging.info('Using GiHub')
        git = GitHubConnector(
            os.environ["OTTM_SMC_TOKEN"],
            os.environ["OTTM_SOURCE_REPO"],
            os.environ["OTTM_CURRENT_BRANCH"],
            session,
            project.project_id,
            repo_dir)
    elif os.environ["OTTM_SOURCE_REPO_SMC"] == "gitlab":
        logging.info('Using GitLab')
        git = GitLabConnector(
            os.environ["OTTM_SMC_BASE_URL"],
            os.environ["OTTM_SMC_TOKEN"],
            os.environ["OTTM_SOURCE_REPO"],
            os.environ["OTTM_CURRENT_BRANCH"],
            session,
            project.project_id,
            repo_dir)
    else:
        logging.error("Unsupported SCM")
        sys.exit('Unsupported SCM')

    git.populate_db()
    # if we use code maat git.setup_aliases(os.environ["OTTM_AUTHOR_ALIAS"])

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
        #jp = JPeekConnector(directory=repo_dir, session=session, version=version)
        #jp.analyze_source_code()

@click.command()
def main():
    pass

if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    logging.info('python: ' + platform.python_version())
    logging.info('system: ' + platform.system())
    logging.info('machine: ' + platform.machine())

    # Setup database
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

    # Setup command line options
    cli(obj={})
