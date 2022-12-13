import logging
import sys
from datetime import datetime
from os.path import exists

import pandas as pd
import click

from metrics.versions import compute_version_metrics
from models.version import Version
from models.issue import Issue


class FlatFileImporter:
    """
    Import CSV file data to the database
    """
    def __init__(self, file_path:str, target_table:str, overwrite:bool, session, config) -> None:
        """
        Constructor

        Parameters:
        -----------
        session : Session
            SQLAlchemy session
        file_path : str
            Fullpath of import file
        target_table : str
            Database table for the import
        overwrite : boolean
            Overwrite database table
        """
        self.session = session
        self.file_path = file_path
        self.target_table = target_table
        self.overwrite = overwrite
        self.configuration = config

    def import_from_csv(self) -> None:
        """
        Import CSV to the database
        """
        logging.info('import_from_csv')
        if self.target_table and str(self.target_table).lower() in ["issue", "version"]:
            if self.file_path and exists(self.file_path):
                # Read CSV file
                csv_data = pd.read_csv(self.file_path).to_dict('records')

                # Import Version
                if str(self.target_table).capitalize() == "Version":
                    # Overwrite option
                    if self.overwrite:
                        self.session.query(Version).delete()
                        click.echo('Overwrite Version table')

                    for version in csv_data:
                        if all(item in list(version.keys()) for item in ['tag', 'start_date', 'end_date']):
                            newVersion=Version(
                                                project_id=version['project_id'],
                                                name=version["name"], 
                                                tag=version["tag"], 
                                                start_date=datetime.strptime(version["start_date"], '%Y-%m-%d %H:%M:%S.%f'), 
                                                end_date=datetime.strptime(version["end_date"], '%Y-%m-%d %H:%M:%S.%f'), 
                                                )
                            
                            try:
                                self.session.add(newVersion)
                                compute_version_metrics(self.session, self.configuration.current_branch, newVersion.project_id)
                                click.echo('Importing ' + str(len(csv_data)) + ' version(s) on database')
                            except Exception:
                                logging.error(Exception)
                        else:
                            logging.error("CSV file no contain minimal mandatory fields")
                            sys.exit('CSV file no contain minimal mandatory fields')

                # Import Issue
                if str(self.target_table).capitalize() == "Issue":
                    # Overwrite option
                    if self.overwrite:
                        self.session.query(Issue).delete()
                        click.echo('Overwrite Issue table')

                    for issue in csv_data:
                        if all(item in list(issue.keys()) for item in ['number', 'created_at', 'updated_at']):
                            newIssue=Issue(
                                            project_id=issue['project_id'],
                                            number=issue["number"],
                                            title=issue["title"],
                                            created_at=datetime.strptime(issue["created_at"], '%Y-%m-%d %H:%M:%S.%f'),
                                            updated_at=datetime.strptime(issue["updated_at"], '%Y-%m-%d %H:%M:%S.%f'))

                            try:
                                self.session.add(newIssue)
                                click.echo('Importing ' + str(len(csv_data)) + ' issue(s) on database')
                            except Exception:
                                logging.error(Exception)
                        else:
                            logging.error("CSV file no contain minimal mandatory fields")
                            sys.exit('CSV file no contain minimal mandatory fields')  

                self.session.commit()
            else:
                logging.error('File not found')
                sys.exit('File not found')
        else:
            logging.error('Target table not found')
            sys.exit('Target table not found')
