import logging

import pandas as pd
from sqlalchemy import desc
from sqlalchemy.sql import func

from configuration import Configuration
from models.version import Version
from models.commit import Commit
from models.issue import Issue
from utils.timeit import timeit

@timeit
def compute_version_metrics(session, current:str, project_id:int):
    """
    Compute version related metics:
    - Rough volume of changes (total lines)
    - Number of issues
    - Bug velocity
    - Average seniorship of the team

    Parameters:
    - session : Session
        SQLAlchemy session
    - current : str
        Current branch being developed
    project_id : int
        Project Identifier
    """
    versions = session.query(Version).filter(Version.project_id == project_id).all()

    for version in versions:
        # Count the number of issues that occurred between the start and end dates
        bugs_count = session.query(Issue).filter(
            Issue.created_at.between(version.start_date, version.end_date)).filter(Issue.project_id == project_id).count()

        # Compute the bug velocity of the release
        delta = version.end_date - version.start_date
        days = delta.days
        if days > 0:
            bug_velo_release = bugs_count / days
        else:
            bug_velo_release = bugs_count

        # Compute a rough estimate of the total changes
        rough_changes = session.query(
            func.sum(Commit.lines).label("total_changes")
        ).filter(Commit.date.between(version.start_date, version.end_date)).filter(Commit.project_id == project_id).scalar()

        # Compute the average seniorship of the team
        team_members = session.query(Commit.committer).filter(
            Commit.date.between(version.start_date, version.end_date)
        ).filter(Commit.project_id == project_id).group_by(Commit.committer).all()
        seniority_total = 0
        for member in team_members:
            first_commit = session.query(
                func.min(Commit.date).label("date")
            ).filter(Commit.committer == member[0]).scalar()
            delta = version.end_date - first_commit
            seniority = delta.days
            seniority_total += seniority
        seniority_avg = seniority_total / max(len(team_members), 1)

        version.bugs=bugs_count
        version.changes=rough_changes
        version.avg_team_xp=seniority_avg
        version.bug_velocity=bug_velo_release
        session.commit()
