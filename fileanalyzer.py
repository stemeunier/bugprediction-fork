import logging
from models.issue import Issue
from models.version import Version
from models.commit import Commit
import lizard
from datetime import datetime
from sqlalchemy.sql import func
from utils.proglang import guess_programing_language
import glob

class FileAnalyzer:
    """Connector to Lizard
    TODO: in fact this connector should be renamed and reporpose as we parse all the files of a version
    We should compute all custom metrics for performance issue
    
    Attributes:
    -----------
     - token        Token for the GitHub API
     - repo         GitHub repository
     - session      Database connection managed by sqlachemy
     - project_id   Identifier of the project
    """

    def __init__(self, directory, session, version_id):
        self.directory = directory
        self.session = session
        self.version_id = version_id
        self.supported_langs = ["C","C++","Java","C#","JavaScript","TypeScript",
            "Objective-C","Swift","Python","Ruby","TTCN-3","PHP","Scala",
            "GDScript","Golang","Lua","Rust","Fortran","Kotlin"]

    def analyze_source_code(self):
        """
        Recursivily analyse a folder containing source files
        """
        logging.info('analyze_source_code')

        # TODO: we should take into account the inclusion/exclusion env var
        # TODO: we should analyze only the main language ?
        # Be aware that glob.glob does not match dotfiles (pathlib.glob does)
        for filename in glob.iglob(self.directory + '/**/**', recursive=True):
            print(filename)
            lang = guess_programing_language(filename)
            print(lang)
            if lang in self.supported_langs:
                count_total = 0
                count_blank = 0
                with open(filename) as fp:
                    for line in fp:
                        count_total += 1
                        if not line.strip():
                            count_blank += 1
                        
                i = lizard.analyze_file(filename)
                comments = count_total - count_blank - i.nloc
                comments_ratio = round((comments / i.nloc) * 100)
                nb_functions = len(i.function_list)
                print("count_total", count_total)
                print("count_blank", count_blank)
                print("comments", comments)
                print(f"comments_ratio = {comments_ratio}%")
                print("nloc", i.nloc)
                print("nb functions", nb_functions)
                print("tokens", i.token_count)
                sum_complexity = 0
                avg_complexity = 0
                if nb_functions>0:
                    for function in i.function_list:
                        sum_complexity += function.cyclomatic_complexity
                    avg_complexity = round(sum_complexity / nb_functions, 2)
                print("avg_complexity", avg_complexity)
                # TODO : when we will compute the global cyclomatic complexity, the files with cc=0
                #        must not be taken into account for the average


                # Lizard returns :
                # the nloc (lines of code without comments),
                # CCN (cyclomatic complexity number),
                # token count of functions.
                # parameter count of functions.

            print ('----------------------------------------------------')
            # files = []
            # for issue in issues:
            #     bugs.append(
            #         Issue(
            #             project_id = self.project_id,
            #             title = issue.title,
            #             number = issue.number,
            #             created_at = issue.created_at
            #         )
            #     )
            # self.session.add_all(bugs)
            # self.session.commit()


