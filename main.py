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
from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv

from container import Container
from configuration import Configuration
from models.project import Project
from models.version import Version
from models.issue import Issue
from models.metric import Metric
from models.model import Model
from models.database import setup_database
from connectors.ck import CkConnector
from connectors.jpeek import JPeekConnector
from connectors.codemaat import CodeMaatConnector
from connectors.fileanalyzer import FileAnalyzer
from connectors.gitfactory import GitConnectorFactory
from connectors.git import GitConnector
from exporters.html import HtmlExporter
from exporters import flatfile
from importers.flatfile import FlatFileImporter
from ml.mlfactory import MlFactory
from utils.dirs import TmpDirCopyFilteredWithEnv

session = None
project = None
configuration = None

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
    os.makedirs(output, exist_ok=True)
    exporter = flatfile.FlatFileExporter(session, project.project_id, output)
    if format == 'csv':
        exporter.export_to_csv("metrics.csv")
    elif format == 'parquet':
        exporter.export_to_parquet("metrics.parquet")

@cli.command()
@click.option('--output', default='.', help='Destination folder')
@click.option('--report-name', default='release', help='Path of file')
@click.pass_context
def report(ctx, output, report_name):
    """Create a basic HTML report"""
    exporter = HtmlExporter(session, output)
    if report_name == "churn":
        exporter.generate_churn_report(project, 'churn.html')
    elif report_name == "release":
        exporter.generate_release_report(project, 'release.html')
    else:
        click.echo("This report doesn't exist")
    pass

@cli.command(name="import")
@click.option('--target-table', is_flag=True, help='Target table in database for the import')
@click.option('--file-path', is_flag=True, help='Path of file')
@click.option('--overwrite', is_flag=True, default=False, help='Overwrite database table')
@click.pass_context
def import_file(ctx, target_table, file_path, overwrite):
    """Import file into tables"""
    importer = FlatFileImporter(session, file_path, target_table, overwrite)
    importer.import_from_csv()

@cli.command()
@click.option('--model-name', default='bugvelocity', help='Name of the model')
@click.pass_context
def train(ctx, model_name):
    """Train a model"""
    model = MlFactory.create_ml_model(model_name, session, project.project_id)
    model.train()
    click.echo("Model was trained")

@cli.command()
@click.option('--model-name', default='bugvelocity', help='Name of the model')
@click.pass_context
def predict(ctx, model_name):
    """Predict next value with a trained model"""
    model = MlFactory.create_ml_model(model_name, session, project.project_id)
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
    trained_models = session.query(Model.name).filter(Model.project_id == project.project_id).all()
    trained_models = [r for r, in trained_models]

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
        project=configuration.source_project,
        language=configuration.language,
        scm=configuration.source_repo_smc,
        repo=configuration.source_repo_url,
        release=configuration.current_branch,
        versions=versions_count,
        issues=issues_count,
        metrics=metrics_count,
        models=", ".join(trained_models)
        )
    click.echo(out)

@cli.command()
@click.pass_context
def check(ctx):
    """Check the consistency of the configuration and perform basic tests"""
    pass

@cli.command()
@click.option('--skip-version', is_flag=True, default=False, help="Skip populate Version")
@click.pass_context
def populate(ctx, skip_version):
    """Populate the database with the provided configuration"""

    # Checkout, execute the tool and inject CSV result into the database
    # with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_dir = tempfile.mkdtemp()
    logging.info('created temporary directory: ' + tmp_dir)

    # Clone the repository
    process = subprocess.run(["git", "clone", configuration.source_repo_url],
                             stdout=subprocess.PIPE,
                             cwd=tmp_dir)
    logging.info('Executed command line: ' + ' '.join(process.args))
    repo_dir = os.path.join(tmp_dir, configuration.source_project)

    git: GitConnector = GitConnectorFactory.create_git_connector(
        session,
        project.project_id,
        repo_dir
    )

    git.populate_db(skip_version)
    # if we use code maat git.setup_aliases(configuration.author_alias)

    # List the versions and checkout each one of them
    versions = session.query(Version).filter(Version.project_id == project.project_id).all()
    for version in versions:
        process = subprocess.run(["git", "checkout", version.tag],
                                 stdout=subprocess.PIPE,
                                 cwd=repo_dir)
        logging.info('Executed command line: ' + ' '.join(process.args))

        with TmpDirCopyFilteredWithEnv(repo_dir) as tmp_work_dir:

            # Get statistics from git log with codemaat
            # codemaat = CodeMaatConnector(repo_dir, session, version)
            # codemaat.analyze_git_log()

            # Get metrics with CK
            ck = CkConnector(directory=tmp_work_dir, session=session, version=version)
            ck.analyze_source_code()

            # Get statistics with lizard
            lizard = FileAnalyzer(directory=tmp_work_dir, session=session, version=version)
            lizard.analyze_source_code()

            # Get metrics with JPeek
            # jp = JPeekConnector(directory=tmp_work_dir, session=session, version=version)
            # jp.analyze_source_code()

@click.command()
@inject
def main():
    pass

if __name__ == '__main__':
    load_dotenv()
    configuration = Configuration()
    container = Container()
    container.wire(modules=[__name__])

    logging.basicConfig(level=configuration.log_level)
    logging.info('python: ' + platform.python_version())
    logging.info('system: ' + platform.system())
    logging.info('machine: ' + platform.machine())

    # Setup database
    engine = db.create_engine(configuration.target_database)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    setup_database(engine)

    project = session.query(Project).filter(Project.name == configuration.source_project).first()
    if not project:
        project = Project(name=configuration.source_project,
                        repo=configuration.source_repo,
                        language=configuration.language)
        session.add(project)
        session.commit()

    # Setup command line options
    cli(obj={})
