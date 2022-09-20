import logging
import os
from os.path import exists
import tempfile
import subprocess
import pandas as pd

from configuration import Configuration
from models.metric import Metric
from utils.math import Math
from utils.timeit import timeit

class CkConnector:
    """
    Connector to CK CLI tool
    https://github.com/mauricioaniche/ck

    Attributes:
    -----------
        - directory   Full path to a cloned GIT repository
        - session     Connection to a database managed by sqlalchemy
        - version     Sqlalchemy object representing a Version
    """

    def __init__(self, directory, session, version):
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
            self.generate_ck_files()
            self.compute_metrics()
        else:
            logging.info('CK analysis already done for this version')

    @timeit
    def generate_ck_files(self):
        """
        Generate CK files with the CK analysis tool
        """
        logging.info('CK::generate_ck_files')
        exclude_dir = ""
        for folder in self.configuration.exclude_folders.split(";"):
            exclude_dir += os.path.join(self.directory, folder) + " "

        # Execute java -jar ck-0.7.1.jar .  .
        process = subprocess.run(["java", "-jar",
                                  self.configuration.code_ck_path,
                                  self.directory, "."])

        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Command return code ' + str(process.returncode))

    def __compute_mean(self, metric, csv_file):
        tmp = csv_file[metric].tolist()
        return Math.get_rounded_mean(tmp)

    @timeit
    def compute_metrics(self):
        """
        Compute CK metrics. As the metrics were computed at the file or function level,
        we need to compute the average for the repository.
        """
        logging.info('CK::compute_metrics')
        
        if (exists("class.csv") and exists("method.csv") and exists("field.csv") and exists("variable.csv")):
            try:
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

                # Create metric object with CK values
                metric = Metric(
                    version_id=self.version.version_id,
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

                # Save metrics values into the database
                self.session.add(metric)
                self.session.commit()
                logging.info("CK metrics added to database for version " + self.version.tag)
            except pd.errors.EmptyDataError:
                logging.error("No columns to parse from CK report /version " + self.version.tag)
            except:
                logging.error("An error occured while reading CK report for version " + self.version.tag)
        else:
            logging.error("An error occured while generating CK report for version " + self.version.tag)
