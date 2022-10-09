from dependency_injector import containers, providers
from configuration import Configuration

class Container(containers.DeclarativeContainer):
    # config
    configuration: Configuration = providers.Singleton()

    # database

