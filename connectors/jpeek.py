import logging
import subprocess
import pandas as pd
import os
import tempfile

from configuration import Configuration
from models.metric import Metric
from utils.timeit import timeit

class JPeekConnector:
    """
    Connector to Jpeek CLI tool
    https://github.com/cqfn/jpeek

    Attributes:
    -----------
        - directory   Full path to a cloned GIT repository
        - session     Connection to a database managed by sqlalchemy
        - version     Sqlalchemy object representing a Version
    """

    def __init__(self, directory, session, version) -> None:
        self.directory = directory
        self.session = session
        self.version = version
        self.configuration = Configuration()

    def analyze_source_code(self):
        """
        Analyze the repository by using CK analysis tool
        """
        logging.info('CK::analyze_repo')
        # Test if metrics have been already generated for this version
        metric = self.session.query(Metric).filter(Metric.version_id == self.version.version_id).first()
        if not metric:
            logging.info('JPeek creates metrics for this version')
            self.create_metric_values()
        else:
            if metric.jp_camc is None:
                logging.info('Adding compute_metrics analysis for this version')
                self.complete_metric_values(metric)
            else:
                logging.info('compute_metrics analysis already done for this version')

    def create_metric_values(self):
        """
        Insert a new set of Lizard metrics into the database
        """
        metric = Metric()
        metric = self.compute_metrics(metric)
        metric.version_id = self.version.version_id
        self.session.add(metric)
        self.session.commit()
        logging.info("JPeek metrics added to database for version " + self.version.tag)

    def complete_metric_values(self, metric: Metric):
        """
        Analyze a folder containing source files
        """
        new_metric = self.compute_metrics(metric)
        metric.jp_camc = new_metric.jp_camc
        metric.jp_lcom = new_metric.jp_lcom
        metric.jp_mmac = new_metric.jp_mmac
        metric.jp_nhd = new_metric.jp_nhd
        metric.jp_scom = new_metric.jp_scom
        self.session.commit()

    @timeit
    def compute_metrics(self, metric: Metric) -> Metric:
        """
        Compute metrics with JPeek
        Insert the values into the database
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Launch the JPeek utility and output values into a temporay directory
            process = subprocess.run(["java", "-jar",
                                    self.configuration.code_jpeek_path, "-t", tmp_dir,
                                    "-s", self.directory, "--overwrite"])
            logging.info('Executed command line: ' + ' '.join(process.args))
            logging.info('Command return code ' + str(process.returncode))

            xml_camc = pd.read_xml(os.path.join(tmp_dir, "CAMC.xml"))
            xml_lcom = pd.read_xml(os.path.join(tmp_dir, "LCOM5.xml"))
            xml_mmac = pd.read_xml(os.path.join(tmp_dir, "MMAC.xml"))
            xml_nhd = pd.read_xml(os.path.join(tmp_dir, "NHD.xml"))
            xml_scom = pd.read_xml(os.path.join(tmp_dir, "SCOM.xml"))

            # Calculate mean JPeek values
            metric.jp_camc = self.compute_mean('mean', xml_camc)
            metric.jp_lcom = self.compute_mean('mean', xml_lcom)
            metric.jp_mmac = self.compute_mean('mean', xml_mmac)
            metric.jp_nhd = self.compute_mean('mean', xml_nhd)
            metric.jp_scom = self.compute_mean('mean', xml_scom)

            return metric

    def compute_mean(self, metric, xml_file):
        tmp = xml_file[metric].tolist()
        return round(sum(tmp) / len(tmp), 2)
