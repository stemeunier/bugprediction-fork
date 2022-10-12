import os
import logging

class Configuration:

    def __init__(self):
        self.exclude_versions = os.environ["OTTM_EXCLUDE_VERSIONS"]
        self.include_versions = os.environ["OTTM_INCLUDE_VERSIONS"]
        
        if "OTTM_EXCLUDE_FOLDERS" in os.environ and os.environ["OTTM_EXCLUDE_FOLDERS"]:
            self.exclude_folders = os.environ["OTTM_EXCLUDE_FOLDERS"].split(";")
        else:
            self.exclude_folders = []

        if "OTTM_INCLUDE_FOLDERS" in os.environ and os.environ["OTTM_INCLUDE_FOLDERS"]:
            self.include_folders = os.environ["OTTM_INCLUDE_FOLDERS"].split(";")
        else:
            self.include_folders = []
        
        if "OTTM_LOG_LEVEL" in os.environ:
            log_level = os.environ["OTTM_LOG_LEVEL"].upper()
            if log_level == "CRITICAL": self.log_level = logging.CRITICAL
            elif log_level == "ERROR": self.log_level = logging.ERROR
            elif log_level == "WARNING": self.log_level = logging.WARNING
            elif log_level == "INFO": self.log_level = logging.INFO
            elif log_level == "DEBUG": self.log_level = logging.DEBUG
            elif log_level == "NOTSET": self.log_level = logging.NOTSET
            else: self.log_level = logging.INFO
        else:
            self.log_level = logging.INFO

        self.code_smc_path = os.environ["OTTM_SMC_PATH"]
        self.code_maat_path = os.environ["OTTM_CODE_MAAT_PATH"]
        self.code_ck_path = os.environ["OTTM_CODE_CK_PATH"]
        self.code_jpeek_path = os.environ["OTTM_CODE_JPEEK_PATH"]

        self.source_project = os.environ["OTTM_SOURCE_PROJECT"]
        self.current_branch = os.environ["OTTM_CURRENT_BRANCH"]
        self.author_alias = os.environ["OTTM_AUTHOR_ALIAS"]
        self.language = os.environ["OTTM_LANGUAGE"]

        self.target_database = os.environ["OTTM_TARGET_DATABASE"]

        self.source_repo_smc = os.environ["OTTM_SOURCE_REPO_SMC"]
        self.source_repo = os.environ["OTTM_SOURCE_REPO"]
        self.smc_base_url = os.environ["OTTM_SMC_BASE_URL"]
        self.source_repo_url = os.environ["OTTM_SOURCE_REPO_URL"]
        self.smc_token = os.environ["OTTM_SMC_TOKEN"]

        if "OTTM_ISSUE_TAGS" in os.environ:
            self.issue_tags = os.environ["OTTM_ISSUE_TAGS"].split(",")
        else:
            self.issue_tags = []

        if "OTTM_EXCLUDE_ISSSUERS" in os.environ:
            self.exclude_issuers = os.environ["OTTM_EXCLUDE_ISSSUERS"].split(",")
        else:
            self.exclude_issuers = []

        if "OTTM_EXCLUDE_AUTHORS" in os.environ:
            self.exclude_authors = os.environ["OTTM_EXCLUDE_AUTHORS"].split(",")
        else:
            self.exclude_authors = []

        if "OTTM_EXCLUDE_FOLDERS" in os.environ:
            self.exclude_folders = os.environ["OTTM_EXCLUDE_FOLDERS"].split(";")
        else:
            self.exclude_folders = []

        if "OTTM_COMMIT_BAD_MSG" in os.environ:
            self.insignificant_commits_messages = os.environ["OTTM_COMMIT_BAD_MSG"].split(";")
        else:
            self.insignificant_commits_messages = []

        self.legacy_percent = int(os.environ["LEGACY_PERCENT"])
        