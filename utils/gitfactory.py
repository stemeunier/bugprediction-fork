import logging
import sys

from dependency_injector import providers
from dependency_injector.wiring import Provide, inject

from utils.container import Container
from connectors.github import GitHubConnector
from connectors.gitlab import GitLabConnector

class GitConnectorFactory:

    @staticmethod
    @inject
    def create_git_connector(session = Provide[Container.session], 
                             config = Provide[Container.configuration],
                             git_factory_provider = Provide[Container.git_factory_provider.provider]) -> None:
        
        scm = config.source_repo_scm

        if scm == "github":
            logging.info('Using GitHub')
            git_factory_provider.override(
                providers.Factory(
                    GitHubConnector,
                    token = config.scm_token,
                    repo = config.source_repo,
                    current = config.current_branch,
                    session = session,
                    config = config
                )
            )
        
        elif scm == "gitlab":
            logging.info('Using GitLab')
            git_factory_provider.override(
                providers.Factory(
                    GitLabConnector,
                    base_url = config.scm_base_url,
                    token = config.scm_token,
                    repo = config.source_repo,
                    current = config.current_branch,
                    session = session,
                    config = config
                )
            )
        
        else:
            logging.error("Unsupported SCM: {scm}")
            sys.exit('Unsupported SCM')
