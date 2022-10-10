from distutils.version import Version
import logging
import os
import pandas as pd
from kneed import KneeLocator
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from kneed import KneeLocator
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

class MlHtmlExporter:
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
    def generate_kmeans_release_report(self, project:Project, filename:str)->None:
        """
        Generate a report that tries to identifies similar releases based 
        on KMeans algorithm

        Parameters
        ----------
        project : Project
            Project object
        filename : str
            Filename (not fullpath) of the report
        """
        logging.info('Generate KMeans HTML report')
        # Load HTML template
        filename = os.path.join(self.directory, filename)
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates/")

        releases_statement = self.session.query(
                Version.tag,
                Version.name,
                Version.bugs,
                Version.avg_team_xp,
                Version.changes,
                Version.bug_velocity,
                Version.code_churn_avg,
                Metric.lizard_avg_complexity) \
                .order_by(Version.end_date.desc()) \
                .join(Metric, Version.version_id == Metric.version_id) \
                .filter(Version.project_id == project.project_id) \
                .statement
        logging.debug(releases_statement)
        df = pd.read_sql(releases_statement, self.session.get_bind())
        df_tr = df[['avg_team_xp', 'changes', 'bug_velocity', 'code_churn_avg', 'lizard_avg_complexity']]

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_tr.values)

        # Try to determine the number of clusters
        kmeans_kwargs = {
            "init": "random",
            "n_init": 10,
            "max_iter": 300,
            "random_state": 42,
        }
        sse = []
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans.fit(scaled_features)
            sse.append(kmeans.inertia_)
        kl = KneeLocator(
            range(1, 11), sse, curve="convex", direction="decreasing"
        )
        clusters = kl.elbow
        logging.info('The number of clusters: ' + str(clusters))

        # Find the clusters
        kmeans = KMeans(
            init="random",
            n_clusters=clusters,
            n_init=10,
            max_iter=300,
            random_state=42
        )
        kmeans.fit(scaled_features)
        logging.info('The lowest SSE value: ' + str(kmeans.inertia_))
        logging.info('Final locations of the centroid: ' + str(kmeans.cluster_centers_))
        logging.info('The number of iterations required to converge: ' + str(kmeans.n_iter_))

        # Glue back to originaal data
        df['cluster'] = kmeans.labels_

        # Locate the next release as we will mark it in the graphs
        next_release_trace = df.loc[df['name'] == "Next Release"]

        # Append the scatter plot graph with a focus on the next release
        fig = px.scatter(df, x='bug_velocity', y='avg_team_xp', color='cluster', 
                 hover_data=['tag', 'bugs'], template='ggplot2')
        fig.add_traces(
            px.scatter(next_release_trace, x="bug_velocity", y="avg_team_xp", hover_data=['cluster', 'bug_velocity']).update_traces(marker_symbol = 'star', marker_size=20, marker_color="red").data
        )
        fig1_html = fig.to_html(full_html=False, include_plotlyjs=False)

        fig = px.scatter(df, x='bug_velocity', y='changes', color='cluster', 
                 hover_data=['tag', 'bugs'], template='ggplot2')
        fig.add_traces(
            px.scatter(next_release_trace, x="bug_velocity", y="changes", hover_data=['cluster', 'bug_velocity']).update_traces(marker_symbol = 'star', marker_size=20, marker_color="red").data
        )
        fig2_html = fig.to_html(full_html=False, include_plotlyjs=False)

        fig = px.scatter(df, x='bug_velocity', y='code_churn_avg', color='cluster', 
                 hover_data=['tag', 'bugs'], template='ggplot2')
        fig.add_traces(
            px.scatter(next_release_trace, x="bug_velocity", y="code_churn_avg", hover_data=['cluster', 'bug_velocity']).update_traces(marker_symbol = 'star', marker_size=20, marker_color="red").data
        )
        fig3_html = fig.to_html(full_html=False, include_plotlyjs=False)

        data = {
            "project": project,
            "graph_clusters": fig1_html,
            "graph_clusters2": fig2_html,
            "graph_clusters3": fig3_html
        }

        # Render the template and save the output
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("kmeans.html")
        output_text = template.render(data)
        with open(os.path.join(self.directory, filename), "w") as file:
            file.write(output_text)
