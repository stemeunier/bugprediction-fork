import logging
import math

import pandas as pd
from sqlalchemy import desc
from sqlalchemy.sql import func
from sklearn import preprocessing
import pandas as pd
import numpy as np
from pydriller.metrics.process.code_churn import CodeChurn

from models.version import Version
from models.metric import Metric
from models.commit import Commit
from models.issue import Issue
from utils.timeit import timeit
import utils.math as mt

@timeit
def compute_version_metrics(session, repo_dir:str, project_id:int):
    """
    Compute version related metics:
    - Rough volume of changes (total lines)
    - Number of issues
    - Bug velocity
    - Average seniorship of the team
    - Code churn

    Parameters:
    - session : Session
        SQLAlchemy session
    - repo_dir : str
        Local folder where the repository was clones
    - project_id : int
        Project Identifier
    """
    versions = session.query(Version) \
        .filter(Version.project_id == project_id) \
        .order_by(Version.start_date.asc()).all()

    from_commit = session.query(Commit.hash) \
        .filter(Commit.project_id == project_id) \
            .order_by(Commit.date.asc()).first()[0]

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

        # Compute the count, average, and max code churn on the version
        logging.info("Counting churn between " + from_commit + " and " + version.tag)
        metric = CodeChurn(path_to_repo=repo_dir,
                        from_commit=from_commit,
                        to_commit=version.tag)
        files_count = metric.count()
        files_avg = metric.avg()
        files_max = metric.max()
        churn_count = 0
        for file_count in files_count.values():
            churn_count += abs(file_count)
        churn_avg = abs(mt.Math.get_rounded_mean(list(files_avg.values())))
        churn_max = max(list(files_max.values()))
        logging.info('Chrun count: ' + str(churn_count) + ' / Chrun avg: ' + str(churn_avg) + ' / Chrun max: ' + str(churn_max))
        from_commit = version.tag

        version.code_churn_count = churn_count
        version.code_churn_avg = churn_avg
        version.code_churn_max = churn_max
        version.bugs=bugs_count
        version.changes=rough_changes
        version.avg_team_xp=seniority_avg
        version.bug_velocity=bug_velo_release
        session.commit()

@timeit
def assess_next_release_risk(session, project_id:int):
    """
    Assess the risk of deploying the next release by using 
    weighed metrics from version

    Parameters:
    - session : Session
        SQLAlchemy session
    - project_id : int
        Project Identifier
    """

    # Get the version metrics and the average cyclomatic complexity
    metrics_statement = session.query(Version, Metric) \
        .filter(Version.project_id == project_id) \
        .join(Metric, Metric.version_id == Version.version_id) \
        .order_by(Version.start_date.asc()).statement
    logging.debug(metrics_statement)
    df = pd.read_sql(metrics_statement, session.get_bind())

    # TODO : we should Remove outliers in the dataframe
    # while preserving the "Next Release" row
    # cols = ['pdays', 'campaign', 'previous'] # The columns you want to search for outliers in
    # # Calculate quantiles and IQR
    # Q1 = df[cols].quantile(0.25) # Same as np.percentile but maps (0,1) and not (0,100)
    # Q3 = df[cols].quantile(0.75)
    # IQR = Q3 - Q1
    # # Return a boolean array of the rows with (any) non-outlier column values
    # condition = ~((df[cols] < (Q1 - 1.5 * IQR)) | (df[cols] > (Q3 + 1.5 * IQR))).any(axis=1)
    #  ---> or (df['name'] == 'Next Release')
    # # Filter our dataframe based on condition
    # filtered_df = df[condition]

    bug_velocity = np.array(df['bug_velocity'])
    bug_velocity = preprocessing.normalize([bug_velocity])
    changes = np.array(df['changes'])
    changes = preprocessing.normalize([changes])
    avg_team_xp = np.array(df['avg_team_xp'])
    avg_team_xp = preprocessing.normalize([avg_team_xp])
    lizard_avg_complexity = np.array(df['lizard_avg_complexity'])
    lizard_avg_complexity = preprocessing.normalize([lizard_avg_complexity])
    code_churn_avg = np.array(df['code_churn_avg'])
    code_churn_avg = preprocessing.normalize([code_churn_avg])

    scaled_df = pd.DataFrame({
        'bug_velocity': bug_velocity[0],
        'changes': changes[0],
        'avg_team_xp': avg_team_xp[0],
        'lizard_avg_complexity': lizard_avg_complexity[0],
        'code_churn_avg': code_churn_avg[0]
        })

    old_cols = df[["name", "bugs"]]
    scaled_df = scaled_df.join(old_cols)

    scaled_df["risk_assessment"] = (
        (scaled_df["bug_velocity"] * 90) +
         (scaled_df["changes"] * 20) +
         ((1 / scaled_df["avg_team_xp"]) * 0.008) +
         (scaled_df["lizard_avg_complexity"] * 40) +
         (scaled_df["code_churn_avg"] * 20)
    )

    median_risk = scaled_df["risk_assessment"].median()
    max_risk = scaled_df["risk_assessment"].max()
    risk_score = scaled_df.loc[(scaled_df["name"] == "Next Release")]
    return {
        "median": math.ceil(median_risk),
        "max": math.ceil(max_risk),
        "score": math.ceil(risk_score.iloc[0]['risk_assessment'])}
