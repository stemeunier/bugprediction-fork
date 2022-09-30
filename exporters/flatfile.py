from distutils.version import Version
import logging
import os
import pandas as pd

from configuration import Configuration
from models.metric import Metric
from models.version import Version
from utils.timeit import timeit

class FlatFileExporter:
    """
    Export the database to a flat file
    """

    def __init__(self, session, project_id, directory):
        """
        Constructor

        Parameters:
        -----------
        session : Session
            SQLAlchemy session
        project_id : int
            Project Identifier
        directory : str
            Output path
        """
        self.directory = directory
        self.session = session
        self.project_id = project_id
        self.configuration = Configuration()

    @timeit
    def export_to_csv(self, filename):
        """
        Export the database to CSV

        Parameters:
        -----------
        filename : str
            name of the file with extension - not the fullpath
        """
        logging.info('export_to_csv')
        metrics_statement = self.session.query(Version, Metric) \
            .filter(Version.project_id == self.project_id) \
            .join(Metric, Metric.version_id == Version.version_id).statement
        logging.debug(metrics_statement)
        df = pd.read_sql(metrics_statement, self.session.get_bind())
        df.to_csv(os.path.join(self.directory, filename))
        
    @timeit
    def export_to_parquet(self, filename):
        """
        Export the database to a parquet file

        Parameters:
        -----------
        filename : str
            name of the file with extension - not the fullpath
        """
        logging.info('export_to_parquet')
        metrics_statement = self.session.query(Version, Metric) \
            .filter(Version.project_id == self.project_id) \
            .join(Metric, Metric.version_id == Version.version_id).statement
        logging.debug(metrics_statement)
        df = pd.read_sql(metrics_statement, self.session.get_bind())
        df.to_csv(os.path.join(self.directory, filename))
 