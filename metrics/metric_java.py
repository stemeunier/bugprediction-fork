from typing import List
from sqlalchemy.orm import Query

from metrics.metric_common import MetricCommon
from models.metric import Metric

class MetricJava(MetricCommon):

    def _get_ck_metrics_query(self) -> Query:
        return self.session.query(Metric.version_id, Metric.ck_cbo, Metric.ck_cbo_modified, Metric.ck_fan_in,
                                Metric.ck_fan_out, Metric.ck_dit, Metric.ck_noc, Metric.ck_nom, Metric.ck_nopm,
                                Metric.ck_noprm, Metric.ck_num_fields, Metric.ck_num_methods,
                                Metric.ck_num_visible_methods, Metric.ck_nosi, Metric.ck_rfc, Metric.ck_wmc,
                                Metric.ck_loc, Metric.ck_lcom, Metric.ck_qty_loops, Metric.ck_qty_comparisons,
                                Metric.ck_qty_returns, Metric.ck_qty_try_catch, Metric.ck_qty_parenth_exps,
                                Metric.ck_qty_str_literals, Metric.ck_qty_numbers, Metric.ck_qty_math_operations,
                                Metric.ck_qty_math_variables, Metric.ck_qty_nested_blocks,
                                Metric.ck_qty_ano_inner_cls_and_lambda, Metric.ck_qty_unique_words, Metric.ck_numb_log_stmts,
                                Metric.ck_has_javadoc, Metric.ck_modifiers, Metric.ck_usage_vars,
                                Metric.ck_usage_fields, Metric.ck_method_invok)
    
    def _get_language_specific_queries(self) -> List[Query]:
        return [self._get_ck_metrics_query()]
