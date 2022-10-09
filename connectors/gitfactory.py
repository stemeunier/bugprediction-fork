import logging
import sys

from sqlalchemy.orm import sessionmaker

from configuration import Configuration
from connectors.git import GitConnector
from connectors.github import GitHubConnector
from connectors.gitlab import GitLabConnector

class GitConnectorFactory:

    @staticmethod
    def create_git_connector(session: sessionmaker, 
                             project_id: str, repo_dir: str) -> GitConnector:
        
        configuration = Configuration()
        scm = configuration.source_repo_smc

        if scm == "github":
            logging.info('Using GiHub')
            return GitHubConnector(
                configuration.smc_token,
                configuration.source_repo,
                configuration.current_branch,
                session,
                project_id,
                repo_dir
            )
        
        elif scm == "gitlab":
            return GitLabConnector(
                configuration.smc_base_url,
                configuration.smc_token,
                configuration.source_repo,
                configuration.current_branch,
                session,
                project_id,
                repo_dir
            )
        
        else:
            logging.error("Unsupported SCM: {scm}")
            sys.exit('Unsupported SCM')
