import copy
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
from utils.math import Math


class CkConnector:
    def __init__(self, directory):
        self.directory = directory
        self.configuration = Configuration()

    def complete_metric_values(self, metric: Metric) -> Metric:
        self.__generate_ck_files()
        new_metric = self.__compute_metrics(metric)
        return new_metric

    def __generate_ck_files(self):
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

    def __compute_mean(self, metric, csv_file):
        tmp = csv_file[metric].tolist()
        # return Math.get_rounded_mean(tmp)
        # TODO fixme
        return Math.get_rounded_mean(tmp)

    def __compute_metrics(self, metric: Metric) -> Metric:
        # Read csv files
        csv_class = pd.read_csv("class.csv")
        csv_method = pd.read_csv("method.csv")
        csv_field = pd.read_csv("field.csv")
        csv_variable = pd.read_csv("variable.csv")

        # Calculate mean CK values
        wmc = self.__compute_mean('wmc', csv_class)
        dit = self.__compute_mean('dit', csv_class)
        noc = self.__compute_mean('noc', csv_class)
        cbo = self.__compute_mean('cbo', csv_class)
        lcom = self.__compute_mean('lcom', csv_class)
        lcc = self.__compute_mean('lcc', csv_class)
        loc = self.__compute_mean('loc', csv_class)
        fanin = self.__compute_mean('fanin', csv_class)
        fanout = self.__compute_mean('fanout', csv_class)
        nom = self.__compute_mean('totalMethodsQty', csv_class)
        nopm = self.__compute_mean('publicMethodsQty', csv_class)
        noprm = self.__compute_mean('privateMethodsQty', csv_class)
        modifiers = self.__compute_mean('modifiers', csv_class)
        nosi = self.__compute_mean('nosi', csv_class)
        rfc = self.__compute_mean('rfc', csv_class)
        tcc = self.__compute_mean('tcc', csv_class)
        cboModified = self.__compute_mean('cboModified', csv_class)
        lcomModified = self.__compute_mean('lcom*', csv_class)
        returnQty = self.__compute_mean('returnQty', csv_class)
        loopQty = self.__compute_mean('loopQty', csv_class)
        tryCatchQty = self.__compute_mean('tryCatchQty', csv_class)
        parenthesizedExpsQty = self.__compute_mean('parenthesizedExpsQty', csv_class)
        numbersQty = self.__compute_mean('numbersQty', csv_class)
        mathOperationsQty = self.__compute_mean('mathOperationsQty', csv_class)
        maxNestedBlocksQty = self.__compute_mean('maxNestedBlocksQty', csv_class)
        anoInnerLambdaQty = self.__compute_mean('anonymousClassesQty', csv_class) + self.__compute_mean('innerClassesQty', csv_class) + self.__compute_mean('lambdasQty', csv_class)
        uniqueWordsQty = self.__compute_mean('uniqueWordsQty', csv_class)
        logStatementsQty = self.__compute_mean('logStatementsQty', csv_class)
        variablesQty = self.__compute_mean('variablesQty', csv_class)
        comparisonsQty = self.__compute_mean('comparisonsQty', csv_class)
        totalMethodsQty = self.__compute_mean('totalMethodsQty', csv_class)
        visibleMethodsQty = self.__compute_mean('visibleMethodsQty', csv_class)
        totalFieldsQty = self.__compute_mean('totalFieldsQty', csv_class)
        stringLiteralsQty = self.__compute_mean('stringLiteralsQty', csv_class)
        hasJavadoc = self.__compute_mean("hasJavaDoc", csv_method)
        methodsInvokedQty = self.__compute_mean("methodsInvokedQty", csv_method)
        usageFields = self.__compute_mean("usage", csv_field)
        usageVars = self.__compute_mean("usage", csv_variable)


        # metrics = ['wmc', 'dit', 'noc', 'cbo', 'lcom', 'fanin', 'fanout', 'nom', 'nopm', 'noprm']
        # data = [wmc, dit, noc, cbo, lcom, fanin, fanout, nom, nopm, noprm]
        # with open('metrics/metrics_' + version.tag + '.csv', 'w') as f:
        #     writer = csv.writer(f)
        #
        #     writer.writerow(metrics)
        #     writer.writerow(data)

        # Complete metric object with CK values
        new_metric = copy.deepcopy(metric)

        new_metric.ck_wmc=wmc
        new_metric.ck_dit=dit
        new_metric.ck_noc=noc
        new_metric.ck_cbo=cbo
        new_metric.ck_cbo_modified=cboModified
        new_metric.ck_lcom=lcom
        new_metric.ck_lcom_modified=lcomModified
        new_metric.ck_fan_in=fanin
        new_metric.ck_fan_out=fanout
        new_metric.ck_has_javadoc=hasJavadoc
        new_metric.ck_lcc=lcc
        new_metric.ck_loc=loc
        new_metric.ck_modifiers=modifiers
        new_metric.ck_method_invok=methodsInvokedQty
        new_metric.ck_nom=nom
        new_metric.ck_nopm=nopm
        new_metric.ck_noprm=noprm
        new_metric.ck_nosi=nosi
        new_metric.ck_num_fields=totalFieldsQty
        new_metric.ck_numb_log_stmts=logStatementsQty
        new_metric.ck_num_methods=totalMethodsQty
        new_metric.ck_num_visible_methods=visibleMethodsQty
        new_metric.ck_qty_ano_inner_cls_and_lambda=anoInnerLambdaQty
        new_metric.ck_qty_comparisons=comparisonsQty
        new_metric.ck_qty_loops=loopQty
        new_metric.ck_qty_math_operations=mathOperationsQty
        new_metric.ck_qty_math_variables=variablesQty
        new_metric.ck_qty_nested_blocks=maxNestedBlocksQty
        new_metric.ck_qty_numbers=numbersQty
        new_metric.ck_qty_parenth_exps=parenthesizedExpsQty
        new_metric.ck_qty_returns=returnQty
        new_metric.ck_qty_str_literals=stringLiteralsQty
        new_metric.ck_qty_try_catch=tryCatchQty
        new_metric.ck_qty_unique_words=uniqueWordsQty
        new_metric.ck_rfc=rfc
        new_metric.ck_tcc=tcc
        new_metric.ck_usage_fields=usageFields
        new_metric.ck_usage_vars=usageVars

        logging.info("CK metrics added to metric object")

        return new_metric
