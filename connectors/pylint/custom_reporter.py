
from pylint.reporters import BaseReporter
from pylint.message import Message
from pylint.reporters.ureports.nodes import Section
from pylint.utils import LinterStats


class CustomReporter(BaseReporter):
    """
    A custom pylint reporter that does nothing.
    
    This class inherits from `BaseReporter` and overrides several methods to do nothing.
    It is intended to be used as a base class for creating custom reporters that only
    override the methods needed for specific use cases.
    
    Methods
    -------
    handle_message(msg: Message) -> None:
        Overrides the `BaseReporter.handle_message` method to do nothing.
        
    _display(layout: Section) -> None:
        Overrides the `BaseReporter._display` method to do nothing.
        
    display_reports(layout: Section) -> None:
        Overrides the `BaseReporter.display_reports` method to do nothing.
        
    display_messages(layout: Section | None) -> None:
        Overrides the `BaseReporter.display_messages` method to do nothing.
        
    on_close(stats: LinterStats, previous_stats: LinterStats | None) -> None:
        Overrides the `BaseReporter.on_close` method to do nothing.
    """

    def handle_message(self, msg: Message) -> None:
        """Do Nothing"""

    def _display(self, layout: Section) -> None:
        """Do Nothing"""

    def display_reports(self, layout: Section) -> None:
        """Do nothing"""

    def display_messages(self, layout: Section | None) -> None:
        """Do nothing"""
    
    def on_close(self, stats: LinterStats, previous_stats: LinterStats | None) -> None:
        """Do Nothing"""
        
    