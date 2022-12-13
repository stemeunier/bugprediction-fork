import copy
import datetime
import logging
from typing import Dict, List

import pydriller

from models.file import File
from models.commit import Commit
from models.legacy import Legacy
from models.metric import Metric
from models.version import Version
from utils.database import save_file_if_not_found

class LegacyConnector:

    def __init__(self, project_id, directory, version, session, config):
        self.session = session
        self.version = version
        self.project_id = project_id
        self.configuration = config

        self.pydriler_git_repo = pydriller.Git(directory)
        self.files_last_modification = {}
        self.first_commit_date = self.__get_first_commit_date()

    def __get_first_commit_date(self):
        project_first_commit: Commit = self.session.query(Commit) \
                                                   .filter(Commit.project_id == self.project_id) \
                                                   .order_by(Commit.date.asc()) \
                                                   .first()
        return project_first_commit.date

    def get_legacy_files(self, version: Version):
        metric = self.session.query(Metric).filter(Metric.version_id == self.version.version_id).first()
        if metric.nb_legacy_files:
            logging.info('Legacy analysis already done for this version')
        else:
            
            logging.info("Getting modified legacy files for version %s", version.name)
            modified_legacy_files = {}

            commits: List[Commit] = self.session.query(Commit).filter(Commit.project_id == self.project_id) \
                                            .filter(Commit.date >= version.start_date) \
                                            .filter(Commit.date <= version.end_date) \
                                            .order_by(Commit.date.asc()).all()

            for commit in commits:
                logging.debug("Commit %s", commit.hash)

                legacy_time_delta = self.__legacy_time_delta(commit.date)

                commit_details = self.pydriler_git_repo.get_commit(commit.hash)
                new_modified_legacy_files_for_commit = self.get_modified_legacy_files_for_commit(
                    self.files_last_modification, commit_details, legacy_time_delta
                )
                modified_legacy_files = self.get_new_modified_legacy_files_for_version(
                    modified_legacy_files, new_modified_legacy_files_for_commit
                )
                self.files_last_modification = self.get_new_files_last_modification_for_commit(
                    self.files_last_modification, commit_details
                )

            logging.info(f"Version {version.name} : {len(modified_legacy_files)} legacy files modified")
            
            self.__save_legacy_files(modified_legacy_files, version.version_id)
            self.__save_metric(modified_legacy_files, version.version_id)

    def __legacy_time_delta(self, current_commit_date):
        delta_since_first_commit = current_commit_date - self.first_commit_date
        
        # We consider as legacy something that was modified in the first x% days of the project
        x = self.configuration.legacy_percent
        legacy = round(((delta_since_first_commit.days / 100) * x), 1)
        legacy_time_delta = datetime.timedelta(days=legacy)
        return delta_since_first_commit - legacy_time_delta

    @staticmethod
    def get_modified_legacy_files_for_commit(files_last_modification: Dict[str, datetime.datetime], 
                                            commit_details: pydriller.Commit, 
                                            legacy_time_delta: datetime.timedelta) -> List[Dict[str, str]]:

        modified_legacy_files = []

        for modified_file in commit_details.modified_files:

            if modified_file.old_path is None or modified_file.old_path not in files_last_modification:
                continue

            last_modification_date = files_last_modification[modified_file.old_path]

            if commit_details.committer_date - last_modification_date < legacy_time_delta:
                continue

            if modified_file.new_path is None:
                continue

            modified_legacy_files.append({
                "old_path": modified_file.old_path,
                "new_path": modified_file.new_path,
                "filename": modified_file.filename,
            })

        return modified_legacy_files

    @staticmethod
    def get_new_modified_legacy_files_for_version(
                    modified_legacy_files: Dict[str, datetime.datetime], 
                    new_commit_modified_legacy_files: List[Dict[str, str]]) -> Dict[str, datetime.datetime]:

        new_modified_legacy_files = copy.deepcopy(modified_legacy_files)

        for legacy_file in new_commit_modified_legacy_files:
            new_modified_legacy_files.pop(legacy_file["old_path"], None)
            new_modified_legacy_files[legacy_file["new_path"]] = legacy_file

        return new_modified_legacy_files

    @staticmethod
    def get_new_files_last_modification_for_commit(files_last_modification: Dict[str, datetime.datetime], 
                                                commit_details: pydriller.Commit) -> Dict[str, datetime.datetime]:
        
        new_files_last_modification = copy.deepcopy(files_last_modification)

        for modified_file in commit_details.modified_files:
            new_files_last_modification.pop(modified_file.old_path, None)
            new_files_last_modification[modified_file.new_path] = commit_details.committer_date

        return new_files_last_modification

    def __save_legacy_files(self, legacy_files: List[str], version_id: int):
        
        self.__delete_existing_leagcy(version_id)
        
        for legacy_file in legacy_files:
            
            file: File = save_file_if_not_found(self.session, legacy_file)

            legacy = Legacy(version_id=version_id, file_id=file.file_id)
            self.session.add(legacy)
            self.session.commit()

    def __delete_existing_leagcy(self, version_id):
        self.session.query(Legacy).filter(Legacy.version_id == version_id).delete()

    def __save_metric(self, legacy_files: List[str], version_id: int):
        metric = self.session.query(Metric).filter(Metric.version_id == version_id).first()
        
        if not metric:
            metric = Metric(version_id=version_id)
        
        metric.nb_legacy_files = len(legacy_files)
        
        self.session.add(metric)
        self.session.commit()