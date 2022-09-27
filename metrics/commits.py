import logging

import pandas as pd
from sqlalchemy import desc

from configuration import Configuration
from models.version import Version
from models.commit import Commit
from models.issue import Issue
from models.metric import Metric
from models.author import Author
from models.alias import Alias
from utils.timeit import timeit


@timeit
def compute_commit_msg_quality(session, version:Version):
    """
    Compute the message quality for a given version

    Return a dictionary of values:
        nb_commits : number of commits
        valid_commits : number of valid commit messages
        valid_commits_ratio : Percentage of valid commit messages
        empty_commits_ratio : Percentage of empty commit messages
        one_word_commits_ratio: Percentage of commit messages containing only one word
        insignificant_commits_ratio : Percentage of insignificant commits messages
        frequent_messages : Pandas dataframe containing the messages whose frequency > 1. Example :
                Message  Frequency
            0      br          3
            1    link          2
    """
    configuration = Configuration()
    project_id = version.project_id
    commits = session.query(Commit.message).filter(Commit.date.between(version.start_date, version.end_date)) \
        .filter(Commit.project_id == project_id).all()

    # Get statistics on malformed commit messages
    empty_commits_nb = 0
    one_word_commits_nb = 0
    insignificant_commits_nb = 0
    valid_commits_nb = 0
    # Prepare a list of bad commit messages to be removed
    words = [word.lower() for word in configuration.insignificant_commits_messages]

    for commit in commits:
        message = commit.message.lower()
        if commit.message is None or len(commit.message.split()) == 0:
            empty_commits_nb += 1
        elif message is not None and any(elem in message for elem in words):
            insignificant_commits_nb += 1
        elif len(commit.message.split()) == 1:
            one_word_commits_nb += 1
        else:
            valid_commits_nb += 1

    # Get most frequent messages
    commits_statement =  session.query(Commit.message).filter(Commit.date.between(version.start_date, version.end_date)) \
        .filter(Commit.project_id == project_id).statement
    df = pd.read_sql(commits_statement, session.get_bind())
    df = df.value_counts() \
            .reset_index() \
            .sort_index() \
            .reset_index(drop=True)
    df.columns = ['Message', 'Frequency']
    df = df[df['Frequency'] > 1]

    value = dict()
    value["nb_commits"] = len(commits)
    value["valid_commits"] = valid_commits_nb
    value["valid_commits_ratio"] = valid_commits_nb / len(commits)
    value["empty_commits_ratio"] = empty_commits_nb / len(commits)
    value["one_word_commits_ratio"] = one_word_commits_nb / len(commits)
    value["insignificant_commits_ratio"] = insignificant_commits_nb / len(commits)
    value["frequent_messages"] = df

    return value
