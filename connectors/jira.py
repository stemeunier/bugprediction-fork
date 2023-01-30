import logging
import requests
from typing import List
from datetime import timedelta, datetime

from jira import JIRA
from sqlalchemy import desc, update

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
        new_ottm_issues = []

        for issue in jira_issues:

            if issue.fields.reporter not in self.config.exclude_issuers:
                
                updated_issue_date = None
                if hasattr(issue.fields, "updated"):
                        updated_issue_date = date_iso_8601_to_datetime(issue.fields.updated)
                
                existing_issue_id = self.__get_existing_issue_id(issue.key)
                
                if existing_issue_id:
                    logging.info("Issue %s already exists, updating it", existing_issue_id)
                    self.session.execute(
                        update(Issue).where(Issue.issue_id == existing_issue_id) \
                                     .values(title=issue.fields.summary, updated_at=updated_issue_date)
                    )
                else:
                    ottm_issue = Issue(
                        project_id=self.project_id,
                        number=issue.key,
                        title=issue.fields.summary,
                        source="jira",
                        created_at=date_iso_8601_to_datetime(issue.fields.created),
                        updated_at=updated_issue_date,
                    )
                    new_ottm_issues.append(
                        ottm_issue
                    )

        self.session.add_all(new_ottm_issues)
        self.session.commit()

    def __get_existing_issue_id(self, issue_number) -> int:
        
        existing_issue_id = None
        
        existing_issue = self.session.query(Issue) \
                    .filter(Issue.project_id == self.project_id) \
                    .filter(Issue.number == issue_number) \
                    .filter(Issue.source == "jira") \
                    .first() 
        
        if existing_issue: 
            existing_issue_id = existing_issue.issue_id

        return existing_issue_id
