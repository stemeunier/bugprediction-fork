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
from utils.database import get_included_and_current_versions_filter
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

    def __init__(self, directory:str, session:Session, config):
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
        self.configuration = config

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

        excluded_versions = self.configuration.exclude_versions
        included_and_current_versions = get_included_and_current_versions_filter(self.session, self.configuration)

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
                .filter(Version.include_filter(included_and_current_versions)) \
                .filter(Version.exclude_filter(excluded_versions)) \
                .statement
        logging.debug(releases_statement)
        df = pd.read_sql(releases_statement, self.session.get_bind())
        df['bug_velocity'].round(decimals = 2)
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
        next_release_trace = df.loc[df['name'] == self.configuration.next_version_name]

        # Append the scatter plot graph with a focus on the next release
        fig = px.scatter(df, x='bug_velocity', y='avg_team_xp', color='cluster', 
                 hover_data=['tag', 'bugs'], template='ggplot2')
        fig.add_traces(
            px.scatter(next_release_trace, x="bug_velocity", y="avg_team_xp", hover_data=['cluster', 'bug_velocity']).update_traces(marker_symbol = 'star', marker_size=20, marker_color="red").data
        )
        fig1_html = fig.to_html(full_html=False, include_plotlyjs=False)
        fig = px.scatter_matrix(df,
            dimensions=["avg_team_xp", "changes", "code_churn_avg", "lizard_avg_complexity", "bug_velocity"],
            color="bug_velocity", symbol="bug_velocity",
            title="Scatter matrix")

        fig.update_traces(diagonal_visible=False)
        fig.update_layout(
            width=1200,
            height=800,
            font={"size":8}
        )
        fig2_html = fig.to_html(full_html=False, include_plotlyjs=False)

        data = {
            "project": project,
            "graph_clusters": fig1_html,
            "graph_matrix": fig2_html
        }

        # Render the template and save the output
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("kmeans.html")
        output_text = template.render(data)
        with open(filename, "w") as file:
            file.write(output_text)
