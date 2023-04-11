import copy
import glob
import logging
import pathlib
import math
from typing import Iterator, Tuple

import lizard
from lizard_ext.keywords import IGNORED_WORDS

from utils.math import Math
from utils.timeit import timeit
from utils.proglang import guess_programing_language
from models.metric import Metric


class FileAnalyzer:
    """Connector to Lizard
    We should compute all custom metrics for performance issue
    
    Attributes:
    -----------
     - token        Token for the GitHub API
     - repo         GitHub repository
     - project_id   Identifier of the project
    """

    def __init__(self, directory, version, session):
        self.directory = directory
        self.session = session
        self.version = version
        self.__supported_languages = ["C","C++","Java","C#","JavaScript","TypeScript",
            "Objective-C","Swift","Python","Ruby","TTCN-3","PHP","Scala",
            "GDScript","Golang","Lua","Rust","Fortran","Kotlin"]

        self.__nb_loc_values = []
        self.__nb_tokens_values = []
        self.__nb_functions_values = []
        self.__total_complexities_values = []
        self.__average_complexities_values = []
        
        self.__nb_operands_values = []
        self.__unique_operands_values = set()
        self.__nb_operators_values = []
        self.__unique_operators_values = set()

        self.__nb_lines_values = []
        self.__nb_blank_lines_values = []
        self.__nb_comments_values = []

    def analyze_source_code(self):
        """
        Analyze the repository by using Lizard analysis tool
        """
        logging.info('Lizard::analyze_repo')
        # Test if metrics have been already generated for this version
        metric = self.session.query(Metric).filter(Metric.version_id == self.version.version_id).first()
        if not metric:
            logging.info('Lizard create metrics for this version')
            self.create_metric_values()
        else:
            if metric.lizard_total_nloc is None:
                logging.info('Adding Lizard analysis for this version')
                self.complete_metric_values(metric)
            else:
                logging.info('Lizard analysis already done for this version')

    @timeit
    def create_metric_values(self):
        """
        Insert a new set of Lizard metrics into the database
        """
        metric = Metric()
        self.__get_metrics_values_from_source_code()
        metric = self.__transform_values_into_metric(metric)
        metric.version_id = self.version.version_id
        self.session.add(metric)
        self.session.commit()

    @timeit
    def complete_metric_values(self, metric: Metric):
        """
        Analyze a folder containing source files
        """
        self.__get_metrics_values_from_source_code()
        new_metric = self.__transform_values_into_metric(metric)
        metric.lizard_total_nloc = new_metric.lizard_total_nloc

        metric.lizard_avg_nloc = new_metric.lizard_avg_nloc
        metric.lizard_nloc_rt = new_metric.lizard_nloc_rt
        metric.lizard_avg_token = new_metric.lizard_avg_token
        metric.lizard_fun_count  = new_metric.lizard_fun_count 
        metric.lizard_fun_rt = new_metric.lizard_fun_rt
        metric.lizard_total_complexity = new_metric.lizard_total_complexity
        metric.lizard_avg_complexity = new_metric.lizard_avg_complexity
        metric.lizard_total_operands_count = new_metric.lizard_total_operands_count
        metric.lizard_unique_operands_count = new_metric.lizard_unique_operands_count
        metric.lizard_total_operators_count = new_metric.lizard_total_operators_count
        metric.lizard_unique_operators_count = new_metric.lizard_unique_operators_count
        metric.total_comments = new_metric.total_comments
        metric.total_lines = new_metric.total_lines
        metric.total_blank_lines = new_metric.total_blank_lines
        metric.total_comments = new_metric.total_comments
        metric.comments_rt = new_metric.comments_rt
        # Halstead
        metric.halstead_length = new_metric.halstead_length
        metric.halstead_vocabulary = new_metric.halstead_vocabulary
        metric.halstead_volume = new_metric.halstead_volume
        metric.halstead_difficulty = new_metric.halstead_difficulty
        metric.halstead_effort = new_metric.halstead_effort
        metric.halstead_time = new_metric.halstead_time
        metric.halstead_bugs = new_metric.halstead_bugs

        self.session.commit()

    def __get_metrics_values_from_source_code(self):
        for filename in self.__get_supported_language_files():
            
            # lizard

            file_analyze = self.__analyze_file(filename)
            nb_lines, nb_blank_lines = self.__count_lines(filename)

            nb_loc = file_analyze.nloc
            self.__nb_loc_values.append(nb_loc)

            nb_token = file_analyze.token_count
            self.__nb_tokens_values.append(nb_token)

            nb_functions = len(file_analyze.function_list)
            self.__nb_functions_values.append(nb_functions)

            total_complexity = sum((f.cyclomatic_complexity for f in file_analyze.function_list))
            self.__total_complexities_values.append(total_complexity)
            
            average_complexity = file_analyze.average_cyclomatic_complexity
            if average_complexity:
                self.__average_complexities_values.append(average_complexity)


            # operators / operands

            nb_operand = sum(file_analyze.wordCount.values())
            self.__nb_operands_values.append(nb_operand)
            unique_operands = set(file_analyze.wordCount.keys())
            self.__unique_operands_values.update(unique_operands)

            nb_operators = sum(file_analyze.operatorCount.values())
            self.__nb_operators_values.append(nb_operators)
            unique_operators = set(file_analyze.operatorCount.keys())
            self.__unique_operators_values.update(unique_operators)

            # lines / comments
            self.__nb_lines_values.append(nb_lines)

            self.__nb_blank_lines_values.append(nb_blank_lines)

            nb_comments = nb_lines - nb_loc - nb_blank_lines
            self.__nb_comments_values.append(nb_comments)

    def __get_supported_language_files(self) -> Iterator[str]:
        # TODO: we should take into account the inclusion/exclusion env var
        for filename in glob.iglob(self.directory + '/**/**', recursive=True):
            # TODO: in  case of model seperation by language, we should make a 
            # switch according to the language
            file_suffix = pathlib.Path(filename).suffix
            file_language = guess_programing_language(file_suffix)
            if file_language in self.__supported_languages:
                yield filename

    def __analyze_file(self, filename: str):
        extensions = lizard.get_extensions(["wordcount"]) + [LizardExtension()]
        analyze_file = lizard.FileAnalyzer(extensions)
        return analyze_file(filename)

    def __count_lines(self, filename: str) -> Tuple[int, int]:
        nb_lines = 0
        nb_blank_lines = 0
        with open(filename, encoding="utf-8", errors="ignore") as f:
            for line in f:
                nb_lines += 1
                if not line.strip():
                    nb_blank_lines += 1
        return nb_lines, nb_blank_lines

    def __transform_values_into_metric(self, metric: Metric) -> Metric:
        new_metric = copy.deepcopy(metric)

        total_lines = sum(self.__nb_lines_values)

        # lizard
        total_nloc = sum(self.__nb_loc_values)
        new_metric.lizard_total_nloc = total_nloc
        new_metric.lizard_avg_nloc = Math.get_rounded_mean_safe(self.__nb_loc_values)
        new_metric.lizard_nloc_rt = Math.get_rounded_rate(total_nloc, total_lines)
       
        new_metric.lizard_avg_token = Math.get_rounded_mean_safe(self.__nb_tokens_values)
        
        total_nb_functions = sum(self.__nb_functions_values)
        new_metric.lizard_fun_count = total_nb_functions
        new_metric.lizard_fun_rt = Math.get_rounded_rate(total_nb_functions, total_lines)

        new_metric.lizard_total_complexity = sum(self.__total_complexities_values)
        new_metric.lizard_avg_complexity = Math.get_rounded_mean_safe(self.__average_complexities_values)

        # operators /operands        
        new_metric.lizard_total_operands_count = sum(self.__nb_operands_values)
        new_metric.lizard_unique_operands_count = len(self.__unique_operands_values)
        new_metric.lizard_total_operators_count = sum(self.__nb_operators_values)
        new_metric.lizard_unique_operators_count = len(self.__unique_operators_values)

        # lines / comments
        total_comments = sum(self.__nb_comments_values)
        new_metric.total_lines = total_lines
        new_metric.total_blank_lines = sum(self.__nb_blank_lines_values)
        new_metric.total_comments = total_comments
        new_metric.comments_rt = Math.get_rounded_rate(total_comments, total_lines)

        # Compute halstead metrics
        mu1 = new_metric.lizard_unique_operators_count
        mu2 = new_metric.lizard_unique_operands_count
        N1 = new_metric.lizard_total_operators_count
        N2 = new_metric.lizard_total_operands_count
        #Vocabulary
        mu = mu1 + mu2
        #length
        N = N1 + N2
        if mu1 and mu2:
            new_metric.halstead_length = mu1 * math.log(mu1, 2) + mu2 * math.log(mu2, 2)
        else:
            new_metric.halstead_length = 0
        
        new_metric.halstead_vocabulary = mu
        new_metric.halstead_volume = N * math.log(mu, 2) if mu != 0 else 0 # the number of mental comparisons needed to write a program of length N
        new_metric.halstead_difficulty = (mu1 * N2) / float(2 * mu2) if mu2 != 0 else 0
        new_metric.halstead_effort = new_metric.halstead_difficulty * new_metric.halstead_volume
        new_metric.halstead_time = new_metric.halstead_effort / 18.0
        new_metric.halstead_bugs = new_metric.halstead_volume / 3000

        logging.info("Lizard metrics added to metric object")

        return new_metric

class LizardExtension(object):

    ignoreList = IGNORED_WORDS

    def __init__(self):
        self.result = {}

    @staticmethod
    def __call__(tokens, reader):
        '''
        The function will be used in multiple threading tasks.
        So don't store any data with an extension object.
        '''
        reader.context.fileinfo.operatorCount = result = {}
        for token in tokens:
            if token in LizardExtension.ignoreList\
                    and token[0] not in ('"', "'", '#'):
                result[token] = result.get(token, 0) + 1
            yield token
