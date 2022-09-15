import logging
import subprocess
import pandas as pd

from configuration import Configuration

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
        print(xml_camc)

        mean = self.compute_mean('mean', xml_camc)

        print(mean)