import logging
from datetime import datetime

from glpi_api import GLPI
from sqlalchemy import desc, update

from models.issue import Issue
from utils.date import date_hour_to_datetime
from utils.timeit import timeit

class GlpiConnector:

    __item_type = "Ticket"
    __category_type = "ITILCategory"
    __user_type = "User"

    def __init__(self, project_id, session, config) -> None:
        self.config = config
        self.session = session
        self.project_id = project_id
        if self.config.glpi_user_token:
            self.__glpi = GLPI(url=self.config.glpi_base_url,
                            apptoken=self.config.glpi_app_token,
                            auth=self.config.glpi_user_token)
        else:
            self.__glpi = GLPI(url=self.config.glpi_base_url,
                            apptoken=self.config.glpi_app_token,
                            auth=(self.config.glpi_username, self.config.glpi_password))
    
    @timeit
    def create_issues(self):
        """
        Create issues into the database from Glpi Issues
        """
        logging.info('GlpiConnector: create_issues')

        last_issue_date = self.__get_last_sinced_date()

        glpi_issues = self._get_issues(updated_after=last_issue_date)

        logging.info('Syncing ' + str(len(glpi_issues)) + ' issue(s) from Glpi')

        self.__save_issues(glpi_issues)

    def __get_last_sinced_date(self) -> datetime:
        last_issue_date = None

        last_issue = self.session.query(Issue) \
                         .filter(Issue.project_id == self.project_id and Issue.source == 'glpi') \
                         .order_by(desc(Issue.updated_at)).first()
        
        if last_issue:
            last_issue_date = last_issue.updated_at
        
        logging.info("Last issue date from database is : %s", last_issue_date)

        return last_issue_date

    def _get_issues(self, updated_after: datetime=None):

        categories_ids = self.__glpi_get_categories_ids()

        if categories_ids:
            glpi_tickets = []
            for category_id in categories_ids:
                glpi_tickets.extend(
                    self.__glpi.get_all_items(self.__item_type, **{"searchText[itilcategories_id]": category_id})
                )
        else:
            glpi_tickets = self.__glpi.get_all_items(self.__item_type)

        glpi_tickets_filtered_with_date = []
        if updated_after:
            glpi_tickets_filtered_with_date = []

            for ticket in glpi_tickets:
                if date_hour_to_datetime(ticket['date_mod']) > updated_after:
                    glpi_tickets_filtered_with_date.append(ticket)
        else:
            glpi_tickets_filtered_with_date = glpi_tickets

        return glpi_tickets_filtered_with_date

    def __glpi_get_categories_ids(self):

        categories_ids = []

        for category in self.config.glpi_categories:
            itil_categories = self.__glpi.get_all_items(self.__category_type, **{"searchText[name]": category})
            for itil_category in itil_categories:
                categories_ids.append(itil_category["id"])

        return categories_ids
    
    def __save_issues(self, glpi_issues) -> None:
        new_ottm_issues = []

        users_dict = self.__glpi_get_users_dict()

        for issue in glpi_issues:
            if users_dict[issue['users_id_recipient']] not in self.config.exclude_issuers:
                existing_issue_id = self.__get_existing_issue_id(issue['id'])

                if existing_issue_id:
                    logging.info("Issue %s already exists, updating it", existing_issue_id)
                    self.session.execute(
                        update(Issue).where(Issue.issue_id == existing_issue_id) \
                                    .values(title=issue['name'], updated_at=date_hour_to_datetime(issue['date_mod']))
                    )
                else:
                    ottm_issue = Issue(
                        project_id=self.project_id,
                        number=issue['id'],
                        title=issue['name'],
                        source="glpi",
                        created_at=date_hour_to_datetime(issue['date']),
                        updated_at=date_hour_to_datetime(issue['date_mod']),
                    )
                    new_ottm_issues.append(ottm_issue)
        
        self.session.add_all(new_ottm_issues)
        self.session.commit()

    def __glpi_get_users_dict(self):
        glpi_users = self.__glpi.get_all_items(self.__user_type)
        users_dict = {}
        for user in glpi_users:
            users_dict[user["id"]] = user["name"]
        return users_dict

    def __get_existing_issue_id(self, issue_number) -> int:
        existing_issue_id = None

        existing_issue = self.session.query(Issue) \
                    .filter(Issue.project_id == self.project_id) \
                    .filter(Issue.number == issue_number) \
                    .filter(Issue.source == "glpi") \
                    .first()
        
        if existing_issue:
            existing_issue_id = existing_issue.issue_id
        
        return existing_issue_id