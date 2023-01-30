import logging
import requests
from typing import List
from datetime import timedelta, datetime

from jira import JIRA
from sqlalchemy import desc

from models.issue import Issue
from utils.date import date_iso_8601_to_datetime, datetime_to_date_hours_minuts
from utils.timeit import timeit

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class JiraConnector:
    
    def __init__(self, project_id, session, config) -> None:
        self.config = config
        self.session = session
        self.project_id = project_id
        self.__client = JIRA(
                                server=self.config.jira_base_url,
                                basic_auth=(self.config.jira_email, self.config.jira_token))

    @timeit
    def create_issues(self):
        """
        Create issues into the database from Jira Issues
        """
        logging.info('JiraConnector: create_issues')

        last_issue_date = self.__get_last_sinced_date()
        if last_issue_date is not None:
            last_issue_date += timedelta(minutes=1)

        jira_issues = self._get_issues(updated_after=last_issue_date, labels=self.config.issue_tags)
        
        logging.info('Syncing ' + str(len(jira_issues)) + ' issue(s) from Jira')

        self.__save_issues(jira_issues)

    def __get_last_sinced_date(self) -> datetime:

        last_issue_date = None

        last_issue = self.session.query(Issue) \
                         .filter(Issue.project_id == self.project_id and Issue.source == 'jira') \
                         .order_by(desc(Issue.updated_at)).first()

        if last_issue:
            last_issue_date = last_issue.updated_at
        
        logging.info("Last issue date from database is : %s", last_issue_date)

        return last_issue_date

    def _get_issues(self, updated_after: datetime = None, labels: List[str] = None):

        jql_query = self.__get_builded_jql_query(updated_after, labels)

        logging.info("Performing JQL query to get Jira issues : %s", jql_query)

        return self.__client.search_issues(jql_query)
    
    def __get_builded_jql_query(self, updated_after: datetime, labels: List[str]) -> str:

        jql_query = f'project={self.config.jira_project}'

        if labels:
            labels_as_string = ",".join(labels)
            jql_query += f' AND labels IN ({labels_as_string})'

        if updated_after:
            updated_after_formated = datetime_to_date_hours_minuts(updated_after)
            jql_query += f' AND updatedDate >= "{updated_after_formated}"'

        return jql_query

    def __save_issues(self, jira_issues) -> None:
        ottm_issues = []

        for issue in jira_issues:

            if issue.fields.reporter not in self.config.exclude_issuers:
                
                ottm_issue = Issue(
                    project_id=self.project_id,
                    number=issue.key,
                    title=issue.fields.summary,
                    source="jira",
                    created_at=date_iso_8601_to_datetime(issue.fields.created),
                )

                if hasattr(issue.fields, "updated"):
                    ottm_issue.updated_at = date_iso_8601_to_datetime(issue.fields.updated)

                ottm_issues.append(
                    ottm_issue
                )

        self.session.add_all(ottm_issues)
        self.session.commit()