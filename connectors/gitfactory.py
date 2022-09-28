import logging
import sys
from typing import Any, Dict

from sqlalchemy.orm import sessionmaker

from connectors.git import GitConnector
from connectors.github import GitHubConnector
from connectors.gitlab import GitLabConnector

class GitConnectorFactory:

    @staticmethod
    def create_git_connector(env_configs: Dict[str, Any], session: sessionmaker, 
                             project_id: str, repo_dir: str) -> GitConnector:
        
        if env_configs["OTTM_SOURCE_REPO_SMC"] == "github":
            logging.info('Using GiHub')
            return GitHubConnector(
                env_configs["OTTM_SMC_TOKEN"],
                env_configs["OTTM_SOURCE_REPO"],
                env_configs["OTTM_CURRENT_BRANCH"],
                session,
                project_id,
                repo_dir
            )
        
        elif env_configs["OTTM_SOURCE_REPO_SMC"] == "gitlab":
            return GitLabConnector(
                env_configs["OTTM_SMC_BASE_URL"],
                env_configs["OTTM_SMC_TOKEN"],
                env_configs["OTTM_SOURCE_REPO"],
                env_configs["OTTM_CURRENT_BRANCH"],
                session,
                project_id,
                repo_dir
            )
        
        else:
            logging.error("Unsupported SCM: {scm}")
            sys.exit('Unsupported SCM')