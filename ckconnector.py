import csv
import json
import logging
import os
import subprocess
import tempfile
import pandas as pd
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
        # process = subprocess.run(["java", "-jar", self.configuration.code_ck_path,
        # "C:\\Users\\g.dubrasquet-duval\\OTTM\\connectors\\ottm-connector-jira", "."])
        exclude_folders = json.loads(self.configuration.exclude_folders)
        exclude_dir = ""

        for folder in exclude_folders:
            exclude_dir += r"C:\Users\g.dubrasquet-duval\OTTM\connectors\ottm-connector-jira" + folder + " "

        process = subprocess.run(["java", "-jar",
                                  self.configuration.code_ck_path,
                                  "C:\\Users\\g.dubrasquet-duval\\OTTM\\connectors\\ottm-connector-jira",
                                  "false", "0", "false", "./", exclude_dir])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Command return code ' + str(process.returncode))

    def compute_mean(self, metric, csv_file):
        tmp = csv_file[metric].tolist()
        return round(sum(tmp) / len(tmp), 2)

    def compute_metrics(self, version_name):
        csv_class = pd.read_csv("class.csv")

        wmc = self.compute_mean('wmc', csv_class)
        dit = self.compute_mean('dit', csv_class)
        noc = self.compute_mean('noc', csv_class)
        cbo = self.compute_mean('cbo', csv_class)
        lcom = self.compute_mean('lcom', csv_class)
        fanin = self.compute_mean('fanin', csv_class)
        fanout = self.compute_mean('fanout', csv_class)
        nom = self.compute_mean('totalMethodsQty', csv_class)
        nopm = self.compute_mean('publicMethodsQty', csv_class)
        noprm = self.compute_mean('privateMethodsQty', csv_class)

        metrics = ['wmc', 'dit', 'noc', 'cbo', 'lcom', 'fanin', 'fanout', 'nom', 'nopm', 'noprm']
        data = [wmc, dit, noc, cbo, lcom, fanin, fanout, nom, nopm, noprm]
        with open('metrics/metrics_' + version_name + '.csv', 'w') as f:
            writer = csv.writer(f)

            writer.writerow(metrics)
            writer.writerow(data)

        logging.info("CK metrics generated in metrics " + version_name + ".csv")
