from distutils.version import Version
import logging
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import jinja2
from sqlalchemy.orm import Session
import numpy as np

from configuration import Configuration
from models.project import Project
from models.metric import Metric
from models.legacy import Legacy
from models.file import File
from models.version import Version
from utils.database import get_included_and_current_versions_filter
from utils.timeit import timeit
from metrics.commits import compute_commit_msg_quality
from metrics.versions import assess_next_release_risk
from metrics.versions import compute_bugvelocity_last_30_days

class HtmlExporter:
    """
    Generate an HTML report 

    Attributes
    ----------
        directory : str
            Output path of the report
        session : Session
            Sqlalchemy ORM session object
        configuration : Configuration
            Application configuration
    """

    def __init__(self, directory:str, session:Session, configuration: Configuration, model):
        """
        HtmlExporter constructor

        Parameters
        ----------
        session : Session
            Sqlalchemy ORM session object
        directory : str
            Output path of the report
        """
        self.directory = directory
        self.session = session
        self.configuration = configuration
        self.__model = model

    @timeit
    def generate_release_report(self, project:Project, filename:str)->None:
        """
        Generate a report about the next release
        The metrics of this report will help the project manager to
        assess the risk of releasing the next version

        Parameters
        ----------
        project : Project
            Project object
        filename : str
            Filename (not fullpath) of the report
        """
        logging.info('Generate HTML report')

        # Load HTML template
        filename = os.path.join(self.directory, filename)
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/")

        excluded_versions = self.configuration.exclude_versions
        included_versions = self.configuration.include_versions

        releases = self.session.query(Version, Metric) \
                .join(Metric, Version.version_id == Metric.version_id) \
                .order_by(Version.end_date.desc()) \
                .filter(Version.project_id == project.project_id) \
                .filter(Version.name != self.configuration.next_version_name) \
                .filter(Version.include_filter(included_versions)) \
                .filter(Version.exclude_filter(excluded_versions)).all()

        tags = [row.Version.tag for row in releases[0:3]]
        bugs = [row.Version.bugs for row in releases[0:3]]
        changes = [row.Version.changes for row in releases[0:3]]
        avg_team_xp = [row.Version.avg_team_xp for row in releases[0:3]]

        # # Append the graphs about the last three releases
        fig = px.bar(x=tags, y=bugs)
        fig1_html = fig.to_html(full_html=False, include_plotlyjs=False)

        fig = px.bar(x=tags, y=changes)
        fig2_html = fig.to_html(full_html=False, include_plotlyjs=False)
        
        fig = px.bar(x=tags, y=avg_team_xp)
        fig3_html = fig.to_html(full_html=False, include_plotlyjs=False)

        current_release = self.session.query(Version, Metric) \
                .join(Metric, Version.version_id == Metric.version_id) \
                .order_by(Version.end_date.desc()) \
                .filter(Version.project_id == project.project_id) \
                .filter(Version.name == self.configuration.next_version_name).first()

        legacy_files = self.session.query(Legacy, File) \
                .join(File, Legacy.file_id == File.file_id) \
                .filter(Legacy.version_id == current_release.Version.version_id) \
                .all()

        bugs_median = np.median([row.Version.bugs for row in releases][~np.all([row.Version.bugs for row in releases] == 0)])
        changes_median = np.median([row.Version.changes for row in releases][~np.all([row.Version.changes for row in releases] == 0)])
        xp_devs_median = np.median([row.Version.avg_team_xp for row in releases][~np.all([row.Version.avg_team_xp for row in releases] == 0)])
        lizard_avg_complexity_median = np.median([row.Metric.lizard_avg_complexity for row in releases][~np.all([row.Metric.lizard_avg_complexity for row in releases] == 0)])
        code_churn_avg_median = np.median([row.Version.code_churn_avg for row in releases][~np.all([row.Version.code_churn_avg for row in releases] == 0)])

        predicted_bugs = -1
        predicted_bugs = self.__model.predict()

        risk = assess_next_release_risk(self.session, self.configuration, project.project_id)

        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = risk['score'],
            title = {'text': "Risk"},
            delta = {'reference': risk['median'], "valueformat": ".0f"},
            gauge = {'axis': {'range': [0, risk['max']]}},
            domain = {'x': [0, 1], 'y': [0, 1]}
        ))
        fig_risk_html = fig.to_html(full_html=False, include_plotlyjs=False)

        data = {
            "project": project,
            "model_name" : self.__model.name,
            "current_release" : current_release,
            "bugs_median" : bugs_median,
            "changes_median" : changes_median,
            "xp_devs_median" : xp_devs_median,
            "code_churn_avg_median" : code_churn_avg_median,
            "lizard_avg_complexity_median" : lizard_avg_complexity_median,
            "predicted_bugs" : predicted_bugs,
            "legacy_files": legacy_files,
            "graph_bugs": fig1_html,
            "graph_changes": fig2_html,
            "graph_xp": fig3_html,
            "graph_risk": fig_risk_html
        }

        # Render the template and save the output
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("release.html")
        output_text = template.render(data)
        with open(filename, "w") as file:
            file.write(output_text)

    @timeit
    def generate_churn_report(self, project:Project, filename:str)->None:
        """
        Generate a report showing the code churn during the project

        Parameters
        ----------
        project : Project
            Project object
        filename : str
            Filename (not fullpath) of the report
        """
        logging.info('Generate HTML report')
        filename = os.path.join(self.directory, filename)
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/")

        excluded_versions = self.configuration.exclude_versions
        included_and_current_versions = get_included_and_current_versions_filter(self.session, self.configuration)

        code_churn_statement = self.session.query(Version.start_date, Version.code_churn_count, Version.code_churn_max, Version.code_churn_avg) \
                .order_by(Version.end_date.desc()) \
                .filter(Version.project_id == project.project_id) \
                .filter(Version.include_filter(included_and_current_versions)) \
                .filter(Version.exclude_filter(excluded_versions)) \
                .statement
        df = pd.read_sql(code_churn_statement, self.session.get_bind())

        # # Append the graphs about the last three releases
        fig = px.line(df, x="start_date", y=df.columns,
                    hover_data={"start_date": "|%B %d, %Y"},
                    title='Code churn during the project lifespan')
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        fig1_html = fig.to_html(full_html=False, include_plotlyjs=False)

        data = {
            "project": project,
            "graph_churn": fig1_html
        }

        # Render the template and save the output
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("churn.html")
        output_text = template.render(data)
        with open(filename, "w") as file:
            file.write(output_text)

    @timeit
    def generate_bugvelocity_report(self, project:Project, filename:str)->None:
        """
        Generate a report showing the code churn during the project

        Parameters
        ----------
        project : Project
            Project object
        filename : str
            Filename (not fullpath) of the report
        """
        logging.info('Generate HTML report')
        filename = os.path.join(self.directory, filename)
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/")

        # Generate a graph about Bug velocity during the last 30 days
        df = compute_bugvelocity_last_30_days(self.session, project.project_id)
        fig = px.line(df, x="created_at", y=df.columns,
                    hover_data={"created_at": "|%B %d, %Y"},
                    title='Bug velocity during the last 30 days')
        fig.update_xaxes(rangeslider_visible=True)
        fig2_html = fig.to_html(full_html=False, include_plotlyjs=False)

        # Generate a graph about Bug velocity during the project lifespan
        excluded_versions = self.configuration.exclude_versions
        included_and_current_versions = get_included_and_current_versions_filter(self.session, self.configuration)

        bugvelocity_statement = self.session.query(Version.start_date, Version.bug_velocity) \
                .order_by(Version.end_date.desc()) \
                .filter(Version.project_id == project.project_id) \
                .filter(Version.include_filter(included_and_current_versions)) \
                .filter(Version.exclude_filter(excluded_versions)) \
                .statement
        df = pd.read_sql(bugvelocity_statement, self.session.get_bind())

        fig = px.line(df, x="start_date", y=df.columns,
                    hover_data={"start_date": "|%B %d, %Y"},
                    title='Bug velocity during the project lifespan')
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        fig1_html = fig.to_html(full_html=False, include_plotlyjs=False)

        # Send data and generated graph to the template
        data = {
            "project": project,
            "graph_bug_velocity_30_days": fig2_html,
            "graph_bug_velocity": fig1_html
        }

        # Render the template and save the output
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("bugvelocity.html")
        output_text = template.render(data)
        with open(filename, "w") as file:
            file.write(output_text)
