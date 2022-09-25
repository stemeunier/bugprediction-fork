import os


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
            
        self.code_maat_path = os.environ["OTTM_CODE_MAAT_PATH"]
        self.code_ck_path = os.environ["OTTM_CODE_CK_PATH"]
        self.code_jpeek_path = os.environ["OTTM_CODE_JPEEK_PATH"]

        self.source_repo_url = os.environ["OTTM_SOURCE_REPO_URL"]
        self.language = os.environ["OTTM_LANGUAGE"]

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
