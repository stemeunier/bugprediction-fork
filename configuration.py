import os


class Configuration:

    def __init__(self):
        self.filter_issues = os.environ["OTTM_FILTER_ISSUES"]
        self.exclude_versions = os.environ["OTTM_EXCLUDE_VERSIONS"]
        self.include_versions = os.environ["OTTM_INCLUDE_VERSIONS"]
        self.exclude_folders = os.environ["OTTM_EXCLUDE_FOLDERS"]
        self.include_folders = os.environ["OTTM_INCLUDE_FOLDERS"]
        self.issue_tag = os.environ["OTTM_ISSUE_TAG"]
        self.code_maat_path = os.environ["OTTM_CODE_MAAT_PATH"]
        self.code_ck_path = os.environ["OTTM_CODE_CK_PATH"]
        self.code_jpeek_path = os.environ["OTTM_CODE_JPEEK_PATH"]
