import logging
import os
import subprocess
import tempfile

from github import Github

from configuration import Configuration


class CkConnector:
    def __init__(self, directory, session):
        self.directory = directory
        self.session = session
        self.configuration = Configuration()

    def generate_ck_files(self):
        """
        Analyze git log through code churn axis
        """
        # java -jar ck-0.7.1.jar .  .
        process = subprocess.run(["java", "-jar", self.configuration.code_ck_path, self.directory, "."])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Command return code ' + str(process.returncode))
