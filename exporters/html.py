from distutils.version import Version
import logging
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import jinja2
from sqlalchemy.orm import Session

from configuration import Configuration
from models.project import Project
from models.metric import Metric
from models.model import Model
from models.version import Version
from utils.timeit import timeit
from ml.mlfactory import MlFactory
from metrics.commits import compute_commit_msg_quality
from metrics.versions import assess_next_release_risk

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

    def __init__(self, session:Session, directory:str):
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
        self.configuration = Configuration()

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
        filename = os.path.join(self.directory, filename)
        # Example of binding with panda dataframe
        # metrics_statement = self.session.query(Version, Metric).join(Metric, Metric.version_id == Version.version_id).statement
        # logging.debug(metrics_statement)
        # df = pd.read_sql(metrics_statement, self.session.get_bind())
        # Load HTML template
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/")

        last_three_releases = self.session.query(Version) \
                .order_by(Version.end_date.desc()) \
                .filter(Version.project_id == project.project_id) \
                .filter(Version.name != "Next Release").limit(3)

        tags = [row.tag for row in last_three_releases]
        bugs = [row.bugs for row in last_three_releases]
        changes = [row.changes for row in last_three_releases]
        avg_team_xp = [row.avg_team_xp for row in last_three_releases]

        # # Append the graphs about the last three releases
        fig = px.bar(x=tags, y=bugs)
        fig1_html = fig.to_html(full_html=False, include_plotlyjs=False)

        fig = px.bar(x=tags, y=changes)
        fig2_html = fig.to_html(full_html=False, include_plotlyjs=False)
        
        fig = px.bar(x=tags, y=avg_team_xp)
        fig3_html = fig.to_html(full_html=False, include_plotlyjs=False)

        current_release = self.session.query(Version) \
                .order_by(Version.end_date.desc()) \
                .filter(Version.project_id == project.project_id) \
                .filter(Version.name == "Next Release").first()

        trained_models = self.session.query(Model.name).filter(Model.project_id == project.project_id).all()
        trained_models = [r for r, in trained_models]
        predicted_bugs = -1
        model_name = ""
        if 'bugvelocity' in trained_models:
            model_name = "bugvelocity"
            model = MlFactory.create_ml_model(model_name, self.session, project.project_id)
            predicted_bugs = model.predict()
        elif 'codemetrics' in trained_models:
            model_name = "codemetrics"
            model = MlFactory.create_ml_model(model_name, self.session, project.project_id)
            predicted_bugs = model.predict()


        commit_msg_stats = compute_commit_msg_quality(self.session, current_release)

        risk = assess_next_release_risk(self.session, project.project_id)

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
            "model_name" : model_name,
            "current_release" : current_release,
            "predicted_bugs" : predicted_bugs,
            "project": project,
            "graph_bugs": fig1_html,
            "graph_changes": fig2_html,
            "graph_xp": fig3_html,
            "graph_risk": fig_risk_html,
            "commit_msg_stats": commit_msg_stats
        }

        # Render the template and save the output
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("release.html")
        output_text = template.render(data)
        with open(os.path.join(self.directory, filename), "w") as file:
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

        code_churn_statement = self.session.query(Version.start_date, Version.code_churn_count, Version.code_churn_max, Version.code_churn_avg) \
                .order_by(Version.end_date.desc()) \
                .filter(Version.project_id == project.project_id) \
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
        with open(os.path.join(self.directory, filename), "w") as file:
            file.write(output_text)
