import logging
import subprocess
import pandas as pd

from configuration import Configuration
from models.metric import Metric

class JPeekConnector:
    def __init__(self, directory, session) -> None:
        self.directory = directory
        self.session = session
        self.configuration = Configuration()

    def generate_jpeek_files(self):

        print(self.configuration.code_jpeek_path, self.directory)
        process = subprocess.run(["java", "-jar",
                                  self.configuration.code_jpeek_path, "-t", "./jpeek",
                                  "-s", self.directory+"\.","--overwrite"])
    
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Command return code ' + str(process.returncode))

    def compute_mean(self, metric, xml_file):
        tmp = xml_file[metric].tolist()
        return round(sum(tmp) / len(tmp), 2)

    def compute_metrics(self, version):
        # Read xml files
        xml_camc = pd.read_xml("jpeek/CAMC.xml")
        xml_lcom = pd.read_xml("jpeek/LCOM5.xml")
        xml_mmac = pd.read_xml("jpeek/MMAC.xml")
        xml_nhd = pd.read_xml("jpeek/NHD.xml")
        xml_scom = pd.read_xml("jpeek/SCOM.xml")

        # Calculate mean JPeek values
        camc = self.compute_mean('mean', xml_camc)
        lcom = self.compute_mean('mean', xml_lcom)
        mmac = self.compute_mean('mean', xml_mmac)
        nhd = self.compute_mean('mean', xml_nhd)
        scom = self.compute_mean('mean', xml_scom)

        # Create metric object with JPeek values
        metric = Metric(
            version_id = version.version_id,
            jp_camc=camc,
            jp_lcom=lcom,
            jp_mmac=mmac,
            jp_nhd=nhd,
            jp_scom=scom
        )

        # Save metric values to Database
        self.session.add(metric)
        self.session.commit()
        logging.info("JPeek metrics added to database for version " + version.tag)