import logging
from dependency_injector import providers
from dependency_injector.wiring import Provide, inject
from metrics.metric_php import MetricPhp
from metrics.metric_python import MetricPython

from metrics.metric_java import MetricJava
from utils.container import Container


class MetricFactory:

    @staticmethod
    @inject
    def create_metrics(session = Provide[Container.session], 
                        config = Provide[Container.configuration],
                        metric_factory_provider = Provide[Container.metric_factory_provider.provider]) -> None:
        if config.language.lower() == "java":
            logging.info("Fetching Java metrics")
            metric_factory_provider.override(
                providers.Factory(
                    MetricJava,
                    session = session,
                    config = config
                )
            )
        elif config.language.lower() == "php":
            logging.info("Fetching PHP metrics")
            metric_factory_provider.override(
                providers.Factory(
                    MetricPhp,
                    session = session,
                    config = config
                )
            )
        elif config.language.lower() == "python":
            logging.info("Fetching Python metrics")
            metric_factory_provider.override(
                providers.Factory(
                    MetricPython,
                    session = session,
                    config = config
                )
            )
        else:
            logging.error(f"Unsupported language: {config.language}")
            raise Exception('Unsupported language')
