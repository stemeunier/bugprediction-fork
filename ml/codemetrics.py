import logging

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import defer

from ml.ml import ml
from models.metric import Metric
from models.version import Version
from utils.timeit import timeit
from xgboost import XGBRegressor


class CodeMetrics(ml):
    def __init__(self, session, project_id):
        ml.__init__(self, session, project_id)
        self.name = "codemetrics"

    @timeit
    def train(self):
        """Train the model"""

        included_versions = self.configuration.include_versions
        excluded_versions = self.configuration.exclude_versions

        versions_metrics_statement = self.session.query(Version.avg_team_xp, Version.bug_velocity, Version.bugs,
                                   Metric.lizard_total_nloc, Metric.lizard_avg_nloc, Metric.lizard_avg_token,
                                   Metric.lizard_fun_count, Metric.lizard_fun_rt, Metric.lizard_nloc_rt,
                                   Metric.lizard_total_complexity, Metric.lizard_avg_complexity,
                                   Metric.lizard_total_operands_count, Metric.lizard_unique_operands_count,
                                   Metric.lizard_total_operators_count, Metric.lizard_unique_operators_count,
                                   Metric.comments_rt, Metric.total_lines, Metric.total_blank_lines,
                                   Metric.total_comments, Metric.ck_cbo, Metric.ck_cbo_modified, Metric.ck_fan_in,
                                   Metric.ck_fan_out, Metric.ck_dit, Metric.ck_noc, Metric.ck_nom, Metric.ck_nopm,
                                   Metric.ck_noprm, Metric.ck_num_fields, Metric.ck_num_methods,
                                   Metric.ck_num_visible_methods, Metric.ck_nosi, Metric.ck_rfc, Metric.ck_wmc,
                                   Metric.ck_loc, Metric.ck_lcom, Metric.ck_qty_loops, Metric.ck_qty_comparisons,
                                   Metric.ck_qty_returns, Metric.ck_qty_try_catch, Metric.ck_qty_parenth_exps,
                                   Metric.ck_qty_str_literals, Metric.ck_qty_numbers, Metric.ck_qty_math_operations,
                                   Metric.ck_qty_math_variables, Metric.ck_qty_nested_blocks,
                                   Metric.ck_qty_ano_inner_cls_and_lambda, Metric.ck_qty_unique_words, Metric.ck_numb_log_stmts,
                                   Metric.ck_has_javadoc, Metric.ck_modifiers, Metric.ck_usage_vars,
                                   Metric.ck_usage_fields, Metric.ck_method_invok, Metric.halstead_length,
                                   Metric.halstead_vocabulary, Metric.halstead_volume, Metric.halstead_difficulty,
                                   Metric.halstead_effort, Metric.halstead_time, Metric.halstead_bugs). \
            order_by(Version.end_date.desc()). \
            filter(Version.project_id == self.project_id). \
            filter(Version.include_filter(included_versions)). \
            filter(Version.exclude_filter(excluded_versions)). \
            filter(Metric.version_id == Version.version_id). \
            filter(Version.name != self.configuration.next_version_name).statement

        dataframe = pd.read_sql(versions_metrics_statement, self.session.get_bind())
        dataframe = dataframe.dropna(axis=1, how='any', thresh=None, subset=None)
        X = dataframe.drop('bugs', axis=1)
        y = dataframe[['bugs']].values.ravel()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        stand = StandardScaler()

        X_train = stand.fit_transform(X_train)
        X_test = stand.transform(X_test)

        # Model: XGBRegressor
        self.model = XGBRegressor(objective='reg:squarederror',
                                  n_estimators=200,
                                  learning_rate=0.1,
                                  tree_method='exact',
                                  random_state=1043)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        xgbRegressor_predictions = [round(value) for value in y_pred]
        self.mse = mean_squared_error(y_test, xgbRegressor_predictions)
        logging.info("BugVelocity: Mean Square Error : " + str(self.mse))
        self.store()

    @timeit
    def predict(self) -> int:
        """Predict the next value"""
        logging.info("CodeMetrics::predict")
        self.restore()  # unpickle the model
        versions_metrics_statement = self.session.query(Version.avg_team_xp, Version.bug_velocity, Version.bugs,
                                   Metric.lizard_total_nloc, Metric.lizard_avg_nloc, Metric.lizard_avg_token,
                                   Metric.lizard_fun_count, Metric.lizard_fun_rt, Metric.lizard_nloc_rt,
                                   Metric.lizard_total_complexity, Metric.lizard_avg_complexity,
                                   Metric.lizard_total_operands_count, Metric.lizard_unique_operands_count,
                                   Metric.lizard_total_operators_count, Metric.lizard_unique_operators_count,
                                   Metric.comments_rt, Metric.total_lines, Metric.total_blank_lines,
                                   Metric.total_comments, Metric.ck_cbo, Metric.ck_cbo_modified, Metric.ck_fan_in,
                                   Metric.ck_fan_out, Metric.ck_dit, Metric.ck_noc, Metric.ck_nom, Metric.ck_nopm,
                                   Metric.ck_noprm, Metric.ck_num_fields, Metric.ck_num_methods,
                                   Metric.ck_num_visible_methods, Metric.ck_nosi, Metric.ck_rfc, Metric.ck_wmc,
                                   Metric.ck_loc, Metric.ck_lcom, Metric.ck_qty_loops, Metric.ck_qty_comparisons,
                                   Metric.ck_qty_returns, Metric.ck_qty_try_catch, Metric.ck_qty_parenth_exps,
                                   Metric.ck_qty_str_literals, Metric.ck_qty_numbers, Metric.ck_qty_math_operations,
                                   Metric.ck_qty_math_variables, Metric.ck_qty_nested_blocks,
                                   Metric.ck_qty_ano_inner_cls_and_lambda, Metric.ck_qty_unique_words, Metric.ck_numb_log_stmts,
                                   Metric.ck_has_javadoc, Metric.ck_modifiers, Metric.ck_usage_vars,
                                   Metric.ck_usage_fields, Metric.ck_method_invok, Metric.halstead_length,
                                   Metric.halstead_vocabulary, Metric.halstead_volume, Metric.halstead_difficulty,
                                   Metric.halstead_effort, Metric.halstead_time, Metric.halstead_bugs) \
            .filter(Version.project_id == self.project_id) \
            .filter(Metric.version_id == Version.version_id) \
            .order_by(Version.end_date.asc()) \
            .filter(Version.name == self.configuration.next_version_name).statement
        dataframe = pd.read_sql(versions_metrics_statement, self.session.get_bind())
        dataframe = dataframe.iloc[0]

        prediction_dataframe = self.model.predict(dataframe)
        value = round(prediction_dataframe[0])
        return value
