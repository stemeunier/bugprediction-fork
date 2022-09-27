
import logging

import click
import csv
import sys

from datetime import datetime
from models.version import Version
from models.issue import Issue
from utils.savemodel import save_model


class FlatFileImporter:
    """
    Import CSV file data to the database
    """

    def __init__(self, session, filename:str, target_table:str, overwrite:bool) -> None:
        self.session = session
        self.filename = filename
        self.target_table = target_table
        self.overwrite = overwrite

    def import_from_csv(self) -> None:
        """
        Import CSV to the database
        """
        logging.info('import_from_csv')
        if self.target_table and str(self.target_table).lower() in ["alias", "author", "commit", "file", "issue", 
                                                      "metric", "model", "ownership", "project", "version"]:
            # Overwrite option
            if self.overwrite:
                self.session.execute('DELETE FROM {target_table}'.format(target_table=str(self.target_table).capitalize()))
                click.echo('Overwrite ' + str(self.target_table).capitalize() + ' table')

            if self.filename:
                # Read CSV file
                csv_data = list(csv.DictReader(open(self.filename, 'r')))
                
                if str(self.target_table).capitalize() == "Version":
                    for version in csv_data:
                        save_model(self.session, 
                                    Version(
                                        project_id=version['project_id'],
                                        name=version["name"], 
                                        tag=version["tag"], 
                                        start_date=datetime.strptime(version["start_date"], '%Y-%m-%d %H:%M:%S.%f'), 
                                        end_date=datetime.strptime(version["end_date"], '%Y-%m-%d %H:%M:%S.%f'), 
                                        bugs=version["bugs"], 
                                        changes=version["changes"], 
                                        avg_team_xp=version["avg_team_xp"], 
                                        bug_velocity=version["bug_velocity"]
                                    ))
                    click.echo('Importing ' + str(len(csv_data)) + ' version(s) on database')

                if str(self.target_table).capitalize() == "Issue":
                    for issue in csv_data:
                        save_model(self.session,
                                    Issue(
                                        project_id=issue['project_id'],
                                        number=issue["number"],
                                        title=issue["title"],
                                        created_at=datetime.strptime(issue["created_at"], '%Y-%m-%d %H:%M:%S.%f'),
                                        updated_at=datetime.strptime(issue["updated_at"], '%Y-%m-%d %H:%M:%S.%f')
                                    ))
                    click.echo('Importing ' + str(len(csv_data)) + ' issue(s) on database')

                self.session.commit()
            else:
                logging.error('File not found')
                sys.exit('File not found')
        else:
            logging.error('Target table not indicated')
            sys.exit('Target table not indicated')