import logging
from dependency_injector.wiring import Provide, inject
from sqlalchemy.orm import Query

from models.metric import Metric
from models.version import Version
from utils.container import Container


class MetricFactory:

    @staticmethod
    @inject
    def _order_by_filters(
            select_query: Query,
            project_id,
            order_version_date = "asc",
            state = "train",
            config = Provide[Container.configuration]) -> Query:
        """
        Adds the order by and filter statements used for the metrics to the initial select query

        Args:
            - select_query (sqlalchemy.orm.Query): The initial select query to which to add the filters and order by
            - project_id: The project id
            - order_version_date: "asc" or "desc" to order by the version's end date
            - state: "train" or "predict" to choose which versions are filtered
        
        Returns:
            The Query object with filters and order by
        """

        if order_version_date not in ["asc", "desc"]:
            logging.error("MetricFactory::order_version_date can only be 'asc' or 'desc'")
            raise Exception("order_version_date can only be 'asc' or 'desc'")
        if state not in ["train", "predict"]:
            logging.error("MetricFactory::state can only be 'train' or 'predict'")
            raise Exception("state can only be 'train' or 'predict'")

        query = select_query \
            .order_by(Version.end_date.asc() if order_version_date == "asc" else Version.end_date.desc()) \
            .filter(Version.project_id == project_id) \
            .filter(Metric.version_id == Version.version_id)
        
        if state == "train":
            query = query \
                .filter(Version.include_filter(config.include_versions)) \
                .filter(Version.exclude_filter(config.exclude_versions)) \
                .filter(Version.name != config.next_version_name)
        elif state == "predict":
            query = query.filter(Version.name == config.next_version_name)

        return query

    @staticmethod
    @inject
    def _get_version_metrics_query(session = Provide[Container.session]) -> Query:
        return session.query(Version.version_id, Version.avg_team_xp, Version.bug_velocity, Version.bugs)
    
    @staticmethod
    @inject
    def _get_lizard_metrics_query(session = Provide[Container.session]) -> Query:
        return session.query(Metric.version_id, Metric.lizard_total_nloc, Metric.lizard_avg_nloc, Metric.lizard_avg_token,
                                Metric.lizard_fun_count, Metric.lizard_fun_rt, Metric.lizard_nloc_rt,
                                Metric.lizard_total_complexity, Metric.lizard_avg_complexity,
                                Metric.lizard_total_operands_count, Metric.lizard_unique_operands_count,
                                Metric.lizard_total_operators_count, Metric.lizard_unique_operators_count,
                                Metric.comments_rt, Metric.total_lines, Metric.total_blank_lines,
                                Metric.total_comments)
    
    @staticmethod
    @inject
    def _get_ck_metrics_query(session = Provide[Container.session]) -> Query:
        return session.query(Metric.version_id, Metric.ck_cbo, Metric.ck_cbo_modified, Metric.ck_fan_in,
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
    
    @staticmethod
    @inject
    def _get_halstead_metrics_query(session = Provide[Container.session]) -> Query:
        return session.query(Metric.version_id, Metric.halstead_length,Metric.halstead_vocabulary, Metric.halstead_volume, 
                                Metric.halstead_difficulty,Metric.halstead_effort, Metric.halstead_time, 
                                Metric.halstead_bugs)
    
    @staticmethod
    @inject
    def _get_pdepend_metrics_query(session = Provide[Container.session]) -> Query:
        return session.query(Metric.version_id, Metric.pdepend_cbo, Metric.pdepend_fan_out, Metric.pdepend_dit, 
                                Metric.pdepend_nof, Metric.pdepend_noc, Metric.pdepend_nom, 
                                Metric.pdepend_nopm,Metric.pdepend_vars,Metric.pdepend_wmc, 
                                Metric.pdepend_calls, Metric.pdepend_nocc, Metric.pdepend_noom, 
                                Metric.pdepend_noi, Metric.pdepend_nop)
    
    @staticmethod
    @inject
    def _get_radon_metrics_query(session = Provide[Container.session]) -> Query:
        return session.query(Metric.version_id, Metric.radon_cc_total, Metric.radon_cc_avg, Metric.radon_loc_total,
                                Metric.radon_loc_avg, Metric.radon_lloc_total, Metric.radon_lloc_avg,
                                Metric.radon_sloc_total, Metric.radon_sloc_avg, Metric.radon_comments_total,
                                Metric.radon_comments_avg, Metric.radon_docstring_total, Metric.radon_docstring_avg,
                                Metric.radon_blank_total, Metric.radon_blank_avg, Metric.radon_single_comments_total,
                                Metric.radon_single_comments_avg, Metric.radon_noc_total, Metric.radon_noc_avg,
                                Metric.radon_nom_total, Metric.radon_nom_avg, Metric.radon_nof_total,
                                Metric.radon_nof_avg, Metric.radon_class_loc_total, Metric.radon_class_loc_avg,
                                Metric.radon_method_loc_total, Metric.radon_method_loc_avg, Metric.radon_func_loc_total,
                                Metric.radon_func_loc_avg)
    
    @staticmethod
    @inject
    def _get_pylint_metrics_query(session = Provide[Container.session]) -> Query:
        return session.query(Metric.version_id, Metric.pylint_cbo, Metric.pylint_fan_out, Metric.pylint_dit,
                                Metric.pylint_noc, Metric.pylint_nom, Metric.pylint_nof,
                                Metric.pylint_num_field, Metric.pylint_num_returns, Metric.pylint_num_loops,
                                Metric.pylint_num_comparisons, Metric.pylint_num_try_except, Metric.pylint_num_str_literals,
                                Metric.pylint_num_numbers, Metric.pylint_num_math_op, Metric.pylint_num_variable,
                                Metric.pylint_num_inner_cls_and_lambda, Metric.pylint_num_docstring, Metric.pylint_num_import,
                                Metric.pylint_lcc)
    
    @staticmethod
    @inject
    def get_metrics_query(
                        project_id,
                        state = "train",
                        session = Provide[Container.session],
                        config = Provide[Container.configuration]) -> Query:
        """
        Generates the SQLAlchemy query for all the metrics depending on project language

        Args:
            - project_id: The project id
            - state: "train" or "predict" to choose which versions are filtered

        Returns:
            The full Query object
        """

        if state not in ["train", "predict"]:
            logging.error("MetricFactory::state can only be 'train' or 'predict'")
            raise Exception("state can only be 'train' or 'predict'")
        
        if state == "train":
            order = "desc"
        elif state == "predict":
            order = "asc"
        language = config.language

        version_metrics_query = MetricFactory._get_version_metrics_query().subquery()
        lizard_metrics_query = MetricFactory._get_lizard_metrics_query().subquery()
        ck_metrics_query = MetricFactory._get_ck_metrics_query().subquery()
        halstead_metrics_query = MetricFactory._get_halstead_metrics_query().subquery()
        pdepend_metrics_query = MetricFactory._get_pdepend_metrics_query().subquery()
        radon_metrics_query = MetricFactory._get_radon_metrics_query().subquery()
        pylint_metrics_query = MetricFactory._get_pylint_metrics_query().subquery()

        if language.lower() == "java":
            logging.info('MetricFactory::Query for Java language')

            query = session.query(
                # Selects all columns of subqueries except version_id
                # version_id is needed to perform the join statements but we remove it from final output
                *[c for c in version_metrics_query.c if c.name != 'version_id'],
                *[c for c in lizard_metrics_query.c if c.name != 'version_id'],
                *[c for c in ck_metrics_query.c if c.name != 'version_id'],
                *[c for c in halstead_metrics_query.c if c.name != 'version_id']
                # Then joining all tables on version_id starting on the version subquery
            ) \
                .select_from(version_metrics_query) \
                .join(lizard_metrics_query, Version.version_id == lizard_metrics_query.c.version_id) \
                .join(ck_metrics_query, Version.version_id == ck_metrics_query.c.version_id) \
                .join(halstead_metrics_query, Version.version_id == halstead_metrics_query.c.version_id)
            
            return MetricFactory._order_by_filters(query, project_id, order, state)

        elif language.lower() == "php":
            logging.info('MetricFactory::Query for PHP language')

            query = session.query(
                # Selects all columns of subqueries except version_id
                # version_id is needed to perform the join statements but we remove it from final output
                *[c for c in version_metrics_query.c if c.name != 'version_id'],
                *[c for c in lizard_metrics_query.c if c.name != 'version_id'],
                *[c for c in pdepend_metrics_query.c if c.name != 'version_id'],
                *[c for c in halstead_metrics_query.c if c.name != 'version_id']
                # Then joining all tables on version_id starting on the version subquery
            ) \
                .select_from(version_metrics_query) \
                .join(lizard_metrics_query, Version.version_id == lizard_metrics_query.c.version_id) \
                .join(pdepend_metrics_query, Version.version_id == pdepend_metrics_query.c.version_id) \
                .join(halstead_metrics_query, Version.version_id == halstead_metrics_query.c.version_id)

            return MetricFactory._order_by_filters(query, project_id, order, state)

        elif language.lower() == "python":
            logging.info('MetricFactory::Query for Python language')

            query = session.query(
                # Selects all columns of subqueries except version_id
                # version_id is needed to perform the join statements but we remove it from final output
                *[c for c in version_metrics_query.c if c.name != 'version_id'],
                *[c for c in lizard_metrics_query.c if c.name != 'version_id'],
                *[c for c in radon_metrics_query.c if c.name != 'version_id'],
                *[c for c in pylint_metrics_query.c if c.name != 'version_id'],
                *[c for c in halstead_metrics_query.c if c.name != 'version_id']
                # Then joining all tables on version_id starting on the version subquery
            ) \
                .select_from(version_metrics_query) \
                .join(lizard_metrics_query, Version.version_id == lizard_metrics_query.c.version_id) \
                .join(radon_metrics_query, Version.version_id == radon_metrics_query.c.version_id) \
                .join(pylint_metrics_query, Version.version_id == pylint_metrics_query.c.version_id) \
                .join(halstead_metrics_query, Version.version_id == halstead_metrics_query.c.version_id)

            return MetricFactory._order_by_filters(query, project_id, order, state)

        else:
            logging.error(f"Unsupported Language: {language}")
            raise Exception(f"Unsupported Language: {language}")
