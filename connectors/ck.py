import logging
import os
import subprocess
import tempfile
from os.path import exists
import pandas as pd
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
    def __init__(self, directory, version, session, config):
        self.directory = directory
        self.session = session
        self.version = version
        self.configuration = config

    def analyze_source_code(self):
        """
        Analyze the repository by using CK analysis tool
        """
        logging.info('CK::analyze_repo')
        # Test if metrics have been already generated for this version
        metric = self.session.query(Metric).filter(Metric.version_id == self.version.version_id).first()
        if not metric:
            metric = Metric()
        if self.configuration.language.lower() != "java":
            logging.error('CK is only used for Java language')
            raise Exception("CK can only analyze Java code")
        elif not metric.ck_wmc:
            self.compute_metrics(metric)
        else:
            logging.info('CK analysis already done for this version')

    def __compute_mean(self, metric, csv_file):
        tmp = csv_file[metric].tolist()
        return Math.get_rounded_mean_safe(tmp)

    @timeit
    def compute_metrics(self, metric):
        """
        Compute CK metrics. As the metrics were computed at the file or function level,
        we need to compute the average for the repository.
        """
        logging.info('CK::compute_metrics')
        # Read csv files

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Launch the CK utility and output values into a temporary directory
            logging.info('CK::generate_ck_files')

            process = subprocess.run([self.configuration.java_path, "-jar",
                                      self.configuration.code_ck_path,
                                      self.directory, "True", "0", "True", os.path.join(tmp_dir, "")])
            logging.info('Executed command line: ' + ' '.join(process.args))
            logging.info('Command return code ' + str(process.returncode))

            if exists(os.path.join(tmp_dir, "class.csv")) and exists(os.path.join(tmp_dir, "method.csv")) and exists(
                    os.path.join(tmp_dir, "field.csv")) and exists(os.path.join(tmp_dir, "variable.csv")):
                try:
                    logging.info('CK files generated correctly')
                    metric.version_id = self.version.version_id

                    # Read csv files
                    csv_class = pd.read_csv(os.path.join(tmp_dir, "class.csv"))
                    csv_method = pd.read_csv(os.path.join(tmp_dir, "method.csv"))
                    csv_field = pd.read_csv(os.path.join(tmp_dir, "field.csv"))
                    csv_variable = pd.read_csv(os.path.join(tmp_dir, "variable.csv"))

                    # Calculate mean CK values
                    metric.ck_wmc = self.__compute_mean('wmc', csv_class)
                    metric.ck_dit = self.__compute_mean('dit', csv_class)
                    metric.ck_noc = self.__compute_mean('noc', csv_class)
                    metric.ck_cbo = self.__compute_mean('cbo', csv_class)
                    metric.ck_lcom = self.__compute_mean('lcom', csv_class)
                    metric.ck_lcc = self.__compute_mean('lcc', csv_class)
                    metric.ck_loc = self.__compute_mean('loc', csv_class)
                    metric.ck_fan_in = self.__compute_mean('fanin', csv_class)
                    metric.ck_fan_out = self.__compute_mean('fanout', csv_class)
                    metric.ck_nom = self.__compute_mean('totalMethodsQty', csv_class)
                    metric.ck_nopm = self.__compute_mean('publicMethodsQty', csv_class)
                    metric.ck_noprm = self.__compute_mean('privateMethodsQty', csv_class)
                    metric.ck_modifiers = self.__compute_mean('modifiers', csv_class)
                    metric.ck_nosi = self.__compute_mean('nosi', csv_class)
                    metric.ck_rfc = self.__compute_mean('rfc', csv_class)
                    metric.ck_tcc = self.__compute_mean('tcc', csv_class)
                    metric.ck_cbo_modified = self.__compute_mean('cboModified', csv_class)
                    metric.ck_lcom_modified = self.__compute_mean('lcom*', csv_class)
                    metric.ck_qty_returns = self.__compute_mean('returnQty', csv_class)
                    metric.ck_qty_loops = self.__compute_mean('loopQty', csv_class)
                    metric.ck_qty_try_catch = self.__compute_mean('tryCatchQty', csv_class)
                    metric.ck_qty_parenth_exps = self.__compute_mean('parenthesizedExpsQty', csv_class)
                    metric.ck_qty_numbers = self.__compute_mean('numbersQty', csv_class)
                    metric.ck_qty_math_operations = self.__compute_mean('mathOperationsQty', csv_class)
                    metric.ck_qty_nested_blocks = self.__compute_mean('maxNestedBlocksQty', csv_class)
                    metric.ck_qty_ano_inner_cls_and_lambda = self.__compute_mean('anonymousClassesQty', csv_class) + self.__compute_mean(
                        'innerClassesQty', csv_class) + self.__compute_mean('lambdasQty', csv_class)
                    metric.ck_qty_unique_words = self.__compute_mean('uniqueWordsQty', csv_class)
                    metric.ck_numb_log_stmts = self.__compute_mean('logStatementsQty', csv_class)
                    metric.ck_qty_math_variables = self.__compute_mean('variablesQty', csv_class)
                    metric.ck_qty_comparisons = self.__compute_mean('comparisonsQty', csv_class)
                    metric.ck_num_methods = self.__compute_mean('totalMethodsQty', csv_class)
                    metric.ck_num_visible_methods = self.__compute_mean('visibleMethodsQty', csv_class)
                    metric.ck_num_fields = self.__compute_mean('totalFieldsQty', csv_class)
                    metric.ck_qty_str_literals = self.__compute_mean('stringLiteralsQty', csv_class)
                    metric.ck_has_javadoc = self.__compute_mean("hasJavaDoc", csv_method)
                    metric.ck_method_invok = self.__compute_mean("methodsInvokedQty", csv_method)
                    metric.ck_usage_fields = self.__compute_mean("usage", csv_field)
                    metric.ck_usage_vars = self.__compute_mean("usage", csv_variable)

                    # Save metrics values into the database
                    self.session.add(metric)
                    self.session.commit()
                    logging.info("CK metrics added to database for version " + self.version.tag)
                except pd.errors.EmptyDataError:
                    logging.error("No columns to parse from CK report / version " + self.version.tag)
                except Exception as e:
                    logging.error("An error occurred while reading CK report for version " + self.version.tag)
                    logging.error(str(e))
