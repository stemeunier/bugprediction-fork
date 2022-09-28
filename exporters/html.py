from distutils.version import Version
import logging
import os
import pandas as pd
import plotly.express as px
import jinja2
from sqlalchemy.orm import Session

from configuration import Configuration
from models.project import Project
from models.metric import Metric
from models.version import Version
from utils.timeit import timeit

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
    def generate(self, project:Project, filename:str)->None:
        """
        Export the database to CSV

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

        data = {
            "project": project,
            "graph1": fig1_html,
            "graph2": fig2_html,
            "graph3": fig3_html
        }

        # Render the template and save the output
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("simple_report.html")
        output_text = template.render(data)
        with open(os.path.join(self.directory, filename), "w") as file:
            file.write(output_text)
