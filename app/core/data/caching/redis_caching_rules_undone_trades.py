from redis import StrictRedis

from app.core.constants import rules_max_val, rules_min_val, \
    SET_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, SET_RULES_UNDONE_ARREAR_TRADES_COUNTS, SET_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, \
    SET_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, SET_RULES_UNDONE_UNDUE_TRADES_COUNTS, \
    SET_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, T27_RULES_UNDONE_ARREAR_TRADES_COUNTS, \
    V14_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, T26_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, \
    V13_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, H10_RULES_UNDONE_UNDUE_TRADES_COUNTS, \
    V15_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, PARENT
from app.core.services.data_service import DataService
from app.core.services.util import get_score_from_dict, get_score_code_from_dict, add_rule_to_dict


# noinspection DuplicatedCode
class RedisCachingRulesUndoneTrades:
    recreate_caches = True
    rds: StrictRedis = None
    ds: DataService = None

    def __init__(self, rds: StrictRedis, ds: DataService) -> None:
        self.rds = rds
        self.ds = ds

    def cache_rules(self):
        self.cache_rules_undone_arrear_trades_counts_t27()
        self.cache_rules_undone_arrear_trades_total_balance_of_last_year_ratios_v14()
        self.cache_rules_undone_past_due_trades_counts_t26()
        self.cache_rules_undone_past_due_trades_total_balance_of_last_year_ratios_v13()
        self.cache_rules_undone_undue_trades_counts_h10()
        self.cache_rules_undone_undue_trades_total_balance_of_last_year_ratios_v15()

    # ---------------------------- set cache methods ----------------------------------- #
    def cache_rules_undone_arrear_trades_counts_t27(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_UNDONE_ARREAR_TRADES_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_UNDONE_ARREAR_TRADES_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T27_RULES_UNDONE_ARREAR_TRADES_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_UNDONE_ARREAR_TRADES_COUNTS, rdict)
        print('caching rules_undone_arrear_trades_counts are done.')

    def cache_rules_undone_arrear_trades_total_balance_of_last_year_ratios_v14(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS)
        if not bool(self.rds.zcount(SET_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V14_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rdict)
        print('caching rules_undone_arrear_trades_total_balance_of_last_year_ratios are done.')

    def cache_rules_undone_past_due_trades_counts_t26(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_UNDONE_PAST_DUE_TRADES_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T26_RULES_UNDONE_PAST_DUE_TRADES_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, rdict)
        print('caching rules_undone_past_due_trades_counts are done.')

    def cache_rules_undone_past_due_trades_total_balance_of_last_year_ratios_v13(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS)
        if not bool(self.rds.zcount(SET_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V13_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rdict)
        print('caching rules_undone_past_due_trades_total_balance_of_last_year_ratios are done.')

    def cache_rules_undone_undue_trades_counts_h10(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_UNDONE_UNDUE_TRADES_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_UNDONE_UNDUE_TRADES_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: H10_RULES_UNDONE_UNDUE_TRADES_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_UNDONE_UNDUE_TRADES_COUNTS, rdict)
        print('caching rules_undone_undue_trades_counts are done.')

    def cache_rules_undone_undue_trades_total_balance_of_last_year_ratios_v15(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS)
        if not bool(self.rds.zcount(SET_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V15_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rdict)
        print('caching rules_undone_undue_trades_total_balance_of_last_year_ratios are done.')

    # ---------------------------- read cache methods ----------------------------------- #
    def get_score_of_rules_undone_arrear_trades_total_balance_of_last_year_ratios_v14(self, arrear_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, arrear_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_undone_arrear_trades_total_balance_of_last_year_ratios_v14(self, arrear_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, arrear_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_undone_arrear_trades_counts_t27(self, arrear_trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_ARREAR_TRADES_COUNTS, arrear_trades_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_undone_arrear_trades_counts_t27(self, arrear_trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_ARREAR_TRADES_COUNTS, arrear_trades_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_undone_past_due_trades_counts_t26(self, past_due_trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, past_due_trades_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_undone_past_due_trades_counts_t26(self, past_due_trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, past_due_trades_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_undone_past_due_trades_total_balance_of_last_year_ratios_v13(self, past_due_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, past_due_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_undone_past_due_trades_total_balance_of_last_year_ratios_v13(self, past_due_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, past_due_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_undone_undue_trades_counts_h10(self, undue_trades_counts):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_UNDUE_TRADES_COUNTS, undue_trades_counts, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_undone_undue_trades_counts_h10(self, undue_trades_counts):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_UNDUE_TRADES_COUNTS, undue_trades_counts, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_undone_undue_trades_total_balance_of_last_year_ratios_v15(self, undue_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, undue_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_undone_undue_trades_total_balance_of_last_year_ratios_v15(self, undue_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, undue_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)
