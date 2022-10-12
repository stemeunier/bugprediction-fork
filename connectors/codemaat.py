import logging
import subprocess
import os
import tempfile
from datetime import datetime

from sqlalchemy.sql import func
import pandas as pd

from models.issue import Issue
from models.version import Version
from models.commit import Commit
from models.file import File
from models.author import Author
from models.ownership import Ownership
from utils.database import save_file_if_not_found
from configuration import Configuration


class CodeMaatConnector:
    """
    Connector to code maat CLI tool
    https://github.com/adamtornhill/code-maat

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

    def analyze_git_log(self):
        """Populate the database from the GitHub API"""
        # Preserve the sequence below
        logging.info('CodeMaat::populate_db')
        git_log_file = self.create_git_log_file()
        # Test if metrics have been already generated for this version
        ownership = self.session.query(Ownership).filter(Ownership.version_id == self.version.version_id).first()
        if not ownership:
            self.ownership_patterns(git_log_file)
        else:
            logging.info('CodeMaat ownership pattern analysis already done for this version')
        # git_log_file = self.create_git_log_file()
        # self.ownership_patterns(git_log_file)
        # self.number_of_authors_per_module(git_log_file)
        # self.logical_coupling(git_log_file)

    def create_git_log_file(self):
        # Generate the git log for the version : use an intermediary bash file in order to avoid git log printing problems
        logging.info('create_git_log_file')
        git_log_file = tempfile.mkstemp(suffix=".log")[1]
        fd, bsh_file = tempfile.mkstemp(suffix=".bash")
        fh = os.fdopen(fd, "w")
        logging.info('Generate bash script for GIT log file: ' + bsh_file)
        logging.info('Generate GIT log file: ' + git_log_file)
        bsh_stmt = f"cd {self.directory}\n"
        bsh_stmt += "git --no-pager log --all --numstat --date=short --pretty=format:\"--%h--%ad--%aN\" --no-renames"
        bsh_stmt += " --since='" + self.version.start_date.isoformat() + "'"
        bsh_stmt += " --until='" + self.version.end_date.isoformat() + "'"
        bsh_stmt += f">{git_log_file}\n"
        fh.write(bsh_stmt)
        fh.close()
        logging.info('Bash script: ' + bsh_stmt)
        process = subprocess.run(["bash", bsh_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        return git_log_file

    def abs_churn(self, git_log_file):
        """
        Analyze git log through code churn axis
        """
        logging.info('abs_churn = ' + git_log_file)
        output_file = tempfile.mkstemp(suffix=".csv")[1]
        # java -jar ./ext-tools/code-maat-1.0.2.jar -l gitlogfile.log -c git2 -a abs-churn > code-maat-abs-churn.csv
        process = subprocess.run(["java", "-jar", self.configuration.code_maat_path, "-l", git_log_file,
                 "-c", "git2", "-a", "abs-churn", "-o", output_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Code Maat output file: ' + output_file)

    def number_of_authors_per_module(self, git_log_file):
        """
        Analyze git log to find out the number of authors per module
        https://github.com/adamtornhill/code-maat#mining-organizational-metrics
        """
        logging.info('number_of_authors_per_module = ' + git_log_file)
        output_file = tempfile.mkstemp(suffix=".csv")[1]
        process = subprocess.run(["java", "-jar", self.configuration.code_maat_path, "-l", git_log_file,
                 "-c", "git2", "-o", output_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Code Maat output file: ' + output_file)

    def logical_coupling(self, git_log_file):
        """
        Analyze git log to find out the logical coupling
        https://github.com/adamtornhill/code-maat#mining-logical-coupling
        """
        logging.info('logical_coupling = ' + git_log_file)
        output_file = tempfile.mkstemp(suffix=".csv")[1]
        process = subprocess.run(["java", "-jar", self.configuration.code_maat_path, "-l", git_log_file,
                 "-c", "git2", "-a", "coupling", "-o", output_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Code Maat output file: ' + output_file)

    def code_age(self, git_log_file):
        """
        Analyze git log to find out the code age
        https://github.com/adamtornhill/code-maat#calculate-code-age
        """
        logging.info('code_age = ' + git_log_file)
        output_file = tempfile.mkstemp(suffix=".csv")[1]
        process = subprocess.run(["java", "-jar", self.configuration.code_maat_path, "-l", git_log_file,
                 "-c", "git2", "-a", "age", "-o", output_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Code Maat output file: ' + output_file)

    def churn_by_author(self, git_log_file):
        """
        Analyze git log to find out the churn by author
        https://github.com/adamtornhill/code-maat#churn-by-author
        """
        logging.info('churn_by_author = ' + git_log_file)
        output_file = tempfile.mkstemp(suffix=".csv")[1]
        process = subprocess.run(["java", "-jar", self.configuration.code_maat_path, "-l", git_log_file,
                 "-c", "git2", "-a", "author-churn", "-o", output_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Code Maat output file: ' + output_file)

    def churn_by_entity(self, git_log_file):
        """
        Analyze git log to find out the churn by entity
        https://github.com/adamtornhill/code-maat#churn-by-entity
        """
        logging.info('churn_by_entity = ' + git_log_file)
        output_file = tempfile.mkstemp(suffix=".csv")[1]
        process = subprocess.run(["java", "-jar", self.configuration.code_maat_path, "-l", git_log_file,
                 "-c", "git2", "-a", "entity-churn", "-o", output_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Code Maat output file: ' + output_file)

    def ownership_patterns(self, git_log_file):
        """
        Analyze git log to analyze the ownership patterns:
         - Entity ownership
         - Entity effort
        https://github.com/adamtornhill/code-maat#ownership-patterns
        """
        logging.info('ownership_patterns = ' + git_log_file)
        ownership_file = tempfile.mkstemp(suffix=".csv")[1]
        process = subprocess.run(["java", "-jar", self.configuration.code_maat_path, "-l", git_log_file,
                 "-c", "git2", "-a", "entity-ownership", "-o", ownership_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Code Maat output file: ' + ownership_file)

        effort_file = tempfile.mkstemp(suffix=".csv")[1]
        process = subprocess.run(["java", "-jar", self.configuration.code_maat_path, "-l", git_log_file,
                 "-c", "git2", "-a", "entity-effort", "-o", effort_file])
        logging.info('Executed command line: ' + ' '.join(process.args))
        logging.info('Code Maat output file: ' + effort_file)

        # Merge the two CSV / inner join on entity + author
        ownership = pd.read_csv(ownership_file)
        effort = pd.read_csv(effort_file)
        df = pd.merge(ownership, effort, 
                        on=['entity', 'author'], 
                        how='inner')

        # Insert the patterns of ownership into the database
        for index, row in df.iterrows():
            # Create the author if it doesn't exist
            author = self.session.query(Author).filter(Author.name == row['author']).first()
            if not author:
                author = Author(name=row['author'])
                self.session.add(author)
                self.session.commit()

            file = save_file_if_not_found(self.session, row['entity'])

            # Create the pattern
            pattern = Ownership(
                version_id = self.version.version_id,
                file_id = file.file_id,
                author_id = author.author_id,
                added = row['added'],
                deleted = row['deleted'],
                author_revs = row['author-revs'],
                total_revs = row['total-revs']
            )
            self.session.add(pattern)
            self.session.commit()
