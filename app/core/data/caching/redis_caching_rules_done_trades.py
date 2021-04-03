from redis import StrictRedis

from app.core.constants import SET_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rules_max_val, rules_min_val, \
    SET_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, SET_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, \
    SET_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, SET_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, \
    SET_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, SET_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, \
    SET_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, T24_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, \
    T25_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, T22_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, \
    T23_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, H6_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, \
    H7_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, T28_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, \
    V12_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, PARENT
from app.core.services.data_service import DataService
from app.core.services.util import get_score_from_dict, add_rule_to_dict, get_score_code_from_dict


# noinspection DuplicatedCode
class RedisCachingRulesDoneTrades:
    recreate_caches = True
    rds: StrictRedis = None
    ds: DataService = None

    def __init__(self, rds: StrictRedis, ds: DataService) -> None:
        self.rds = rds
        self.ds = ds

    def cache_rules(self):
        self.cache_rules_done_arrear_trades_of_last_3_months_t24()
        self.cache_rules_done_arrear_trades_between_last_3_to_12_months_t25()
        self.cache_rules_done_past_due_trades_of_last_3_months_t22()
        self.cache_rules_done_past_due_trades_between_last_3_to_12_months_t23()
        self.cache_rules_done_timely_trades_of_last_3_months_h6()
        self.cache_rules_done_timely_trades_between_last_3_to_12_months_h7()
        self.cache_rules_done_trades_average_delay_days_t28()
        self.cache_rules_done_trades_average_total_balance_ratios_v12()

    # ---------------------------- set cache methods ----------------------------------- #
    def cache_rules_done_arrear_trades_of_last_3_months_t24(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS)
        if not bool(self.rds.zcount(SET_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T24_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, rdict)
        print('caching rules_done_arrear_trades_of_last_3_months_t24 are done.')

    def cache_rules_done_arrear_trades_between_last_3_to_12_months_t25(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS)

        if not bool(self.rds.zcount(SET_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T25_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rdict)
        print('caching rules_done_arrear_trades_between_last_3_to_12_months_t25 are done.')

    def cache_rules_done_past_due_trades_of_last_3_months_t22(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS)

        if not bool(self.rds.zcount(SET_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T22_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, rdict)
        print('caching rules_done_past_due_trades_of_last_3_months_t22 are done.')

    def cache_rules_done_past_due_trades_between_last_3_to_12_months_t23(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS)

        if not bool(self.rds.zcount(SET_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T23_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rdict)
        print('caching rules_done_past_due_trades_between_last_3_to_12_months_t23 are done.')

    def cache_rules_done_timely_trades_of_last_3_months_h6(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS)

        if not bool(self.rds.zcount(SET_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: H6_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, rdict)
        print('caching rules_done_timely_due_trades_of_last_3_months are done.')

    def cache_rules_done_timely_trades_between_last_3_to_12_months_h7(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS)

        if not bool(self.rds.zcount(SET_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: H7_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rdict)
        print('caching rules_done_timely_trades_between_last_3_to_12_months_h7 are done.')

    def cache_rules_done_trades_average_delay_days_t28(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS)

        if not bool(self.rds.zcount(SET_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T28_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, rdict)
        print('caching rules_done_trades_average_delay_days_t28 are done.')

    def cache_rules_done_trades_average_total_balance_ratios_v12(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS)

        if not bool(self.rds.zcount(SET_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V12_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, rdict)
        print('caching rules_done_trades_average_total_amount_v12 are done.')

    # ---------------------------- read cache methods ----------------------------------- #
    def get_score_of_rules_done_arrear_trades_of_last_3_months_t24(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, trades_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_done_arrear_trades_of_last_3_months_t24(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, trades_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_done_arrear_trades_between_last_3_to_12_months_t25(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, trades_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_done_arrear_trades_between_last_3_to_12_months_t25(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, trades_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_done_past_due_trades_of_last_3_months_t22(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, trades_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_done_past_due_trades_of_last_3_months_t22(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, trades_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_done_past_due_trades_between_last_3_to_12_months_t23(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, trades_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_done_past_due_trades_between_last_3_to_12_months_t23(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, trades_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_done_timely_trades_of_last_3_months_h6(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, trades_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_done_timely_trades_of_last_3_months_h6(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, trades_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_done_timely_trades_between_last_3_to_12_months_h7(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, trades_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_done_timely_trades_between_last_3_to_12_months_h7(self, trades_count):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, trades_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_done_trades_average_delay_days_t28(self, average_delay_days):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, average_delay_days, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_done_trades_average_delay_days_t28(self, average_delay_days):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, average_delay_days, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_done_trades_average_total_balance_ratios_v12(self, average_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, average_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_done_trades_average_total_balance_ratios_v12(self, average_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, average_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)
