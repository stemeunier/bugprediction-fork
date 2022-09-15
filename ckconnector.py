import csv
import json
import logging
import os
import subprocess
import tempfile
import pandas as pd
from github import Github

from configuration import Configuration
from models.metric import Metric


class CkConnector:
    def __init__(self, directory, session):
        self.directory = directory
        self.session = session
        self.configuration = Configuration()

    def generate_ck_files(self):
        """
        Analyze git log through code churn axis
        """
        exclude_folders = json.loads(self.configuration.exclude_folders)
        exclude_dir = ""

        for folder in exclude_folders:
            exclude_dir += r"C:\Users\g.dubrasquet-duval\OTTM\connectors\ottm-connector-jira" + folder + " "

        # Execute java -jar ck-0.7.1.jar .  .
        process = subprocess.run(["java", "-jar", 
                                  self.configuration.code_ck_path,
                                  self.directory, "."])
        """
        process = subprocess.run(["java", "-jar",
                                  self.configuration.code_ck_path,
                                  self.directory,
                                  "false", "0", "false", "./", exclude_dir])
        """
                                  
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Command return code ' + str(process.returncode))

    def compute_mean(self, metric, csv_file):
        tmp = csv_file[metric].tolist()
        return round(sum(tmp) / len(tmp), 2)

    def compute_metrics(self, version):
        # Read csv files
        csv_class = pd.read_csv("class.csv")
        csv_method = pd.read_csv("method.csv")
        csv_field = pd.read_csv("field.csv")
        csv_variable = pd.read_csv("variable.csv")

        # Calculate mean CK values
        wmc = self.compute_mean('wmc', csv_class)
        dit = self.compute_mean('dit', csv_class)
        noc = self.compute_mean('noc', csv_class)
        cbo = self.compute_mean('cbo', csv_class)
        lcom = self.compute_mean('lcom', csv_class)
        lcc = self.compute_mean('lcc', csv_class)
        loc = self.compute_mean('loc', csv_class)
        fanin = self.compute_mean('fanin', csv_class)
        fanout = self.compute_mean('fanout', csv_class)
        nom = self.compute_mean('totalMethodsQty', csv_class)
        nopm = self.compute_mean('publicMethodsQty', csv_class)
        noprm = self.compute_mean('privateMethodsQty', csv_class)
        modifiers = self.compute_mean('modifiers', csv_class)
        nosi = self.compute_mean('nosi', csv_class)
        rfc = self.compute_mean('rfc', csv_class)
        tcc = self.compute_mean('tcc', csv_class)
        cboModified = self.compute_mean('cboModified', csv_class)
        lcomModified = self.compute_mean('lcom*', csv_class)
        returnQty = self.compute_mean('returnQty', csv_class)
        loopQty = self.compute_mean('loopQty', csv_class)
        tryCatchQty = self.compute_mean('tryCatchQty', csv_class)
        parenthesizedExpsQty = self.compute_mean('parenthesizedExpsQty', csv_class)
        numbersQty = self.compute_mean('numbersQty', csv_class)
        mathOperationsQty = self.compute_mean('mathOperationsQty', csv_class)
        maxNestedBlocksQty = self.compute_mean('maxNestedBlocksQty', csv_class)
        anoInnerLambdaQty = self.compute_mean('anonymousClassesQty', csv_class) + self.compute_mean('innerClassesQty', csv_class) + self.compute_mean('lambdasQty', csv_class)
        uniqueWordsQty = self.compute_mean('uniqueWordsQty', csv_class)
        logStatementsQty = self.compute_mean('logStatementsQty', csv_class)
        variablesQty = self.compute_mean('variablesQty', csv_class)
        comparisonsQty = self.compute_mean('comparisonsQty', csv_class)
        totalMethodsQty = self.compute_mean('totalMethodsQty', csv_class)
        visibleMethodsQty = self.compute_mean('visibleMethodsQty', csv_class)
        totalFieldsQty = self.compute_mean('totalFieldsQty', csv_class)
        stringLiteralsQty = self.compute_mean('stringLiteralsQty', csv_class)
        hasJavadoc = self.compute_mean("hasJavaDoc", csv_method)
        methodsInvokedQty = self.compute_mean("methodsInvokedQty", csv_method)
        usageFields = self.compute_mean("usage", csv_field)
        usageVars = self.compute_mean("usage", csv_variable)


        # metrics = ['wmc', 'dit', 'noc', 'cbo', 'lcom', 'fanin', 'fanout', 'nom', 'nopm', 'noprm']
        # data = [wmc, dit, noc, cbo, lcom, fanin, fanout, nom, nopm, noprm]
        # with open('metrics/metrics_' + version.tag + '.csv', 'w') as f:
        #     writer = csv.writer(f)
        #
        #     writer.writerow(metrics)
        #     writer.writerow(data)

        # Create metric object with CK values
        metric = Metric(
            version_id=version.version_id,
            ck_wmc=wmc,
            ck_dit=dit,
            ck_noc=noc,
            ck_cbo=cbo,
            ck_cbo_modified=cboModified,
            ck_lcom=lcom,
            ck_lcom_modified=lcomModified,
            ck_fan_in=fanin,
            ck_fan_out=fanout,
            ck_has_javadoc=hasJavadoc,
            ck_lcc=lcc,
            ck_loc=loc,
            ck_modifiers=modifiers,
            ck_method_invok=methodsInvokedQty,
            ck_nom=nom,
            ck_nopm=nopm,
            ck_noprm=noprm,
            ck_nosi=nosi,
            ck_num_fields=totalFieldsQty,
            ck_numb_log_stmts=logStatementsQty,
            ck_num_methods=totalMethodsQty,
            ck_num_visible_methods=visibleMethodsQty,
            ck_qty_ano_inner_cls_and_lambda=anoInnerLambdaQty,
            ck_qty_comparisons=comparisonsQty,
            ck_qty_loops=loopQty,
            ck_qty_math_operations=mathOperationsQty,
            ck_qty_math_variables=variablesQty,
            ck_qty_nested_blocks=maxNestedBlocksQty,
            ck_qty_numbers=numbersQty,
            ck_qty_parenth_exps=parenthesizedExpsQty,
            ck_qty_returns=returnQty,
            ck_qty_str_literals=stringLiteralsQty,
            ck_qty_try_catch=tryCatchQty,  
            ck_qty_unique_words=uniqueWordsQty,  
            ck_rfc=rfc,
            ck_tcc=tcc,
            ck_usage_fields=usageFields,
            ck_usage_vars=usageVars
        )

        # Save metric values to Database
        self.session.add(metric)
        self.session.commit()
        logging.info("CK metrics added to database fo version " + version.tag)
