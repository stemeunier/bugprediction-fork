import os
import sys
import json
import logging
import platform
import subprocess
import tempfile
from xmlrpc.client import boolean

import click
import sqlalchemy as db
from sqlalchemy.exc import ArgumentError
from dependency_injector.wiring import Provide, inject
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from dependency_injector import providers

from utils.container import Container
from exceptions.configurationvalidation import ConfigurationValidationException
from models.project import Project
from models.version import Version
from models.issue import Issue
from models.metric import Metric
from models.model import Model
from models.database import setup_database
from connectors.git import GitConnector
from utils.mlfactory import MlFactory
from utils.database import get_included_and_current_versions_filter
from utils.dirs import TmpDirCopyFilteredWithEnv
from utils.gitfactory import GitConnectorFactory

def lint_aliases(raw_aliases) -> boolean:
    try:
        aliases = json.loads(raw_aliases)
    except:
        return False

    if not isinstance(aliases, dict):
        return False

    for v in aliases.values():
        if not isinstance(v, list):
            return False

    return True

def check_branch_exists(configuration, repo_dir, branch_name):
    process = subprocess.run([configuration.scm_path, "branch", "-a"],
                             cwd=repo_dir, capture_output=True)

    if not f"remotes/origin/{branch_name}" in process.stdout.decode():
        raise ConfigurationValidationException(f"Branch {branch_name} doesn't exists in this repository")

def instanciate_git_connector(configuration, git_factory_provider, tmp_dir, repo_dir) -> GitConnector:
    """
        Instanciates a git connector and performs first checks
    """
    # Clone the repository
    process = subprocess.run([configuration.scm_path, "clone", configuration.source_repo_url],
                             stdout=subprocess.PIPE,
                             cwd=tmp_dir)
    try:
        process.check_returncode()
    except subprocess.CalledProcessError:
        raise ConfigurationValidationException(f"Failed to clone {configuration.source_repo_url} repository")
    logging.info('Executed command line: ' + ' '.join(process.args))

    if not os.path.isdir(repo_dir):
        raise ConfigurationValidationException(
            f"Project {configuration.source_project} doesn't exist in current repository")

    try:
        git: GitConnector = git_factory_provider(
            project.project_id,
            repo_dir
        )

    except Exception as e:
        raise ConfigurationValidationException(
            f"Error connecting to project {configuration.source_repo} using source code manager: {str(e)}.")

    check_branch_exists(configuration, repo_dir, configuration.current_branch)

    if not lint_aliases(configuration.author_alias):
        raise ConfigurationValidationException(f"Value error for aliases: {configuration.author_alias}")

    return git

@click.group()
@click.pass_context
@inject
def cli(ctx):
    """Datamining on git repository to predict the risk of releasing next version"""
    pass

@cli.command()
@click.option('--output', default='.', help='Destination folder', envvar="OTTM_OUTPUT_FOLDER")
@click.option('--format', default='csv', help='Output format (csv,parquet)', envvar="OTTM_OUTPUT_FORMAT")
@click.pass_context
@inject
def export(ctx, output, format, 
           flat_file_exporter_provider = Provide[Container.flat_file_exporter_provider.provider]):
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
    exporter = flat_file_exporter_provider(project.project_id, output)
    if format == 'csv':
        exporter.export_to_csv("metrics.csv")
    elif format == 'parquet':
        exporter.export_to_parquet("metrics.parquet")
    logging.info(f"Created export {output}/metrics.{format}")

@cli.command()
@click.option('--output', default='.', help='Destination folder', envvar="OTTM_OUTPUT_FOLDER")
@click.option('--report-name', default='release', help='Name of the report (release, churn, bugvelocity)')
@click.pass_context
@inject
def report(ctx, output, report_name,
           html_exporter_provider = Provide[Container.html_exporter_provider.provider],
           ml_html_exporter_provider = Provide[Container.ml_html_exporter_provider.provider]):
    """Create a basic HTML report"""
    MlFactory.create_predicting_ml_model(project.project_id)
    exporter = html_exporter_provider(output)
    os.makedirs(output, exist_ok=True)
    if report_name == "churn":
        exporter.generate_churn_report(project, 'churn.html')
    elif report_name == "release":
        exporter.generate_release_report(project, 'release.html')
    elif report_name == "bugvelocity":
        exporter.generate_bugvelocity_report(project, 'bugvelocity.html')
    elif report_name == "kmeans":
        exporter = ml_html_exporter_provider(output)
        exporter.generate_kmeans_release_report(project, 'kmeans.html')
    else:
        click.echo("This report doesn't exist")
    logging.info(f"Created report {output}/{report_name}.html")

@cli.command(name="import")
@click.option('--target-table', is_flag=True, help='Target table in database for the import')
@click.option('--file-path', is_flag=True, help='Path of file')
@click.option('--overwrite', is_flag=True, default=False, help='Overwrite database table')
@click.pass_context
@inject
def import_file(ctx, target_table, file_path, overwrite,
                flat_file_importer_provider = Provide[Container.flat_file_importer_provider.provider]):
    """Import file into tables"""
    importer = flat_file_importer_provider(file_path, target_table, overwrite)
    importer.import_from_csv()

@cli.command()
@click.option('--model-name', default='bugvelocity', help='Name of the model')
@click.pass_context
@inject
def train(ctx, model_name, ml_factory_provider = Provide[Container.ml_factory_provider.provider]):
    """Train a model"""
    MlFactory.create_training_ml_model(model_name)
    model = ml_factory_provider(project.project_id)
    model.train()
    click.echo("Model was trained")

@cli.command()
@click.option('--model-name', default='bugvelocity', help='Name of the model')
@click.pass_context
@inject
def predict(ctx, model_name, ml_factory_provider = Provide[Container.ml_factory_provider.provider]):
    """Predict next value with a trained model"""
    MlFactory.create_training_ml_model(model_name)
    model = ml_factory_provider(project.project_id)
    value = model.predict()
    click.echo("Predicted value : " + str(value))

@cli.command()
@click.pass_context
@inject
def info(ctx, configuration = Provide[Container.configuration], session = Provide[Container.session]):
    """Provide information about the current configuration
    If these values are not populated, the tool won't work.
    """
    
    excluded_versions = configuration.exclude_versions
    included_and_current_versions = get_included_and_current_versions_filter(session, configuration)
    filtered_version_count = session.query(Version) \
                                    .filter(Version.project_id == project.project_id) \
                                    .filter(Version.include_filter(included_and_current_versions)) \
                                    .filter(Version.exclude_filter(excluded_versions)) \
                                    .count()
    
    total_versions_count = session.query(Version).filter(Version.project_id == project.project_id).count()
    issues_count = session.query(Issue).filter(Issue.project_id == project.project_id).count()
    metrics_count = session.query(Metric).join(Version).filter(Version.project_id == project.project_id).count()
    trained_models = session.query(Model.name).filter(Model.project_id == project.project_id).all()
    trained_models = [r for r, in trained_models]

    out = """ -- OTTM Bug Predictor --
    Project  : {project}
    Language : {language}
    SCM      : {scm} / {repo}
    Release  : {release}
    
    Versions : {versions} ({excluded_versions} filtered)
    Issues   : {issues}
    Metrics  : {metrics}

    Trained models : {models}
    """.format(
        project=configuration.source_project,
        language=configuration.language,
        scm=configuration.source_repo_scm,
        repo=configuration.source_repo_url,
        release=configuration.current_branch,
        versions=filtered_version_count,
        excluded_versions=total_versions_count-filtered_version_count,
        issues=issues_count,
        metrics=metrics_count,
        models=", ".join(trained_models)
        )
    click.echo(out)

@cli.command()
@click.pass_context
@inject
def check(ctx, configuration = Provide[Container.configuration],
          git_factory_provider = Provide[Container.git_factory_provider.provider]):
    """Check the consistency of the configuration and perform basic tests"""
    tmp_dir = tempfile.mkdtemp()
    logging.info('created temporary directory: ' + tmp_dir)
    repo_dir = os.path.join(tmp_dir, configuration.source_project)

    instanciate_git_connector(configuration, git_factory_provider, tmp_dir, repo_dir)

    logging.info("Check OK")

@cli.command()
@click.option('--skip-versions', is_flag=True, default=False, help="Skip the step <populate Version table>")
@click.pass_context
@inject
def populate(ctx, skip_versions, 
             session = Provide[Container.session],
             configuration = Provide[Container.configuration],
             git_factory_provider = Provide[Container.git_factory_provider.provider],
             ck_connector_provider = Provide[Container.ck_connector_provider.provider],
             file_analyzer_provider = Provide[Container.file_analyzer_provider.provider],
             jpeek_connector_provider = Provide[Container.jpeek_connector_provider.provider],
             legacy_connector_provider = Provide[Container.legacy_connector_provider.provider],
             codemaat_connector_provider = Provide[Container.codemaat_connector_provider.provider]):
    """Populate the database with the provided configuration"""

    # Checkout, execute the tool and inject CSV result into the database
    # with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_dir = tempfile.mkdtemp()
    logging.info('created temporary directory: ' + tmp_dir)
    repo_dir = os.path.join(tmp_dir, configuration.source_project)

    git = instanciate_git_connector(configuration, git_factory_provider, tmp_dir, repo_dir)

    git.populate_db(skip_versions)
    # if we use code maat git.setup_aliases(configuration.author_alias)

    # List the versions and checkout each one of them
    versions = session.query(Version).filter(Version.project_id == project.project_id).all()
    for version in versions:
        process = subprocess.run([configuration.scm_path, "checkout", version.tag],
                                 stdout=subprocess.PIPE,
                                 cwd=repo_dir)
        logging.info('Executed command line: ' + ' '.join(process.args))

        with TmpDirCopyFilteredWithEnv(repo_dir, configuration.include_folders, 
                                       configuration.exclude_folders) as tmp_work_dir:

            
            # FIXME : this execution is dependent from previous version
            # So if some versions are ignored in config, the result is wrong 
            legacy = legacy_connector_provider(project.project_id, repo_dir, version)
            legacy.get_legacy_files(version)

            # Get statistics from git log with codemaat
            # codemaat = codemaat_connector_provider(repo_dir, version)
            # codemaat.analyze_git_log()

            # Get metrics with CK
            ck = ck_connector_provider(directory=tmp_work_dir, version=version)
            ck.analyze_source_code()

            # Get statistics with lizard
            lizard = file_analyzer_provider(directory=tmp_work_dir, version=version)
            lizard.analyze_source_code()

            # Get metrics with JPeek
            jp = jpeek_connector_provider(directory=tmp_work_dir, version=version)
            jp.analyze_source_code()

@click.command()
@inject
def main():
    pass

@inject
def configure_logging(config = Provide[Container.configuration]) -> None:
    logging.basicConfig(level=config.log_level)

@inject
def configure_session(container: Container, config = Provide[Container.configuration]) -> None:
    try:
        engine = db.create_engine(config.target_database)
    except ArgumentError as e:
        raise ConfigurationValidationException(f"Error from sqlalchemy : {str(e)}")
    
    Session = sessionmaker()
    Session.configure(bind=engine)
    setup_database(engine)

    container.session.override(
        providers.Singleton(Session)
    )

@inject
def instanciate_project(config = Provide[Container.configuration],
                        session = Provide[Container.session]) -> Project:
    project = session.query(Project).filter(Project.name == config.source_project).first()
    if not project:
        project = Project(name=config.source_project,
                        repo=config.source_repo,
                        language=config.language)
        session.add(project)
        session.commit()
    return project


if __name__ == '__main__':
    try:
        load_dotenv()

        container = Container()
        container.init_resources()
        container.wire(modules=[
            __name__,
            "utils.gitfactory",
            "utils.mlfactory",
        ])

        configure_logging()
        configure_session(container)
        project = instanciate_project()
        GitConnectorFactory.create_git_connector()

        logging.info('python: ' + platform.python_version())
        logging.info('system: ' + platform.system())
        logging.info('machine: ' + platform.machine())
        
        # Setup command line options
        cli(obj={})
    except ConfigurationValidationException as e:
        logging.error("CONFIGURATIONS ERROR")
        logging.error(e.message)
