from sqlalchemy.orm import Query

from metrics.metric_common import MetricCommon
from models.metric import Metric

class MetricPhp(MetricCommon):

    def _get_pdepend_metrics_query(self) -> Query:
        return self.session.query(Metric.version_id, Metric.pdepend_cbo, Metric.pdepend_fan_out, Metric.pdepend_dit, 
                                Metric.pdepend_nof, Metric.pdepend_noc, Metric.pdepend_nom, 
                                Metric.pdepend_nopm,Metric.pdepend_vars,Metric.pdepend_wmc, 
                                Metric.pdepend_calls, Metric.pdepend_nocc, Metric.pdepend_noom, 
                                Metric.pdepend_noi, Metric.pdepend_nop)
    
    def _get_language_specific_query(self) -> Query:
        return [self._get_pdepend_metrics_query()]
    