from redis import StrictRedis

from app.core.constants import V20_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, T34_RULES_LOAN_ARREAR_TOTAL_COUNTS, \
    V16_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, \
    H11_RULES_LOAN_TOTAL_COUNTS, V18_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, V19_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS, \
    T33_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, V21_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, T35_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS, PARENT
from app.core.constants import rules_max_val, rules_min_val, \
    SET_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, SET_RULES_LOAN_ARREAR_TOTAL_COUNTS, SET_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, \
    SET_RULES_LOAN_TOTAL_COUNTS, SET_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, SET_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS, \
    SET_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, SET_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, SET_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS
from app.core.services.data_service import DataService
from app.core.services.util import get_score_from_dict, add_rule_to_dict, get_score_code_from_dict


# noinspection DuplicatedCode
class RedisCachingRulesLoans:
    recreate_caches = True
    rds: StrictRedis = None
    ds: DataService = None

    def __init__(self, rds: StrictRedis, ds: DataService) -> None:
        self.rds = rds
        self.ds = ds

    def cache_rules(self):
        self.cache_rules_arrear_loans_total_balance_ratios_v20()
        self.cache_rules_arrear_loans_total_counts_t34()
        self.cache_rules_loan_monthly_installments_total_balance_ratios_v16()
        self.cache_rules_loans_total_counts_h11()
        self.cache_rules_overdue_loans_total_balance_ratios_v18()
        self.cache_rules_past_due_loans_total_balance_ratios_v19()
        self.cache_rules_past_due_loans_total_counts_t33()
        self.cache_rules_suspicious_loans_total_balance_ratios_v21()
        self.cache_rules_suspicious_loans_total_counts_t35()

    # ---------------------------- set cache methods ----------------------------------- #
    def cache_rules_arrear_loans_total_balance_ratios_v20(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V20_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, rdict)
        print('caching rules_arrear_loans_total_balance_ratios are done.')

    def cache_rules_arrear_loans_total_counts_t34(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_ARREAR_TOTAL_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_ARREAR_TOTAL_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T34_RULES_LOAN_ARREAR_TOTAL_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_ARREAR_TOTAL_COUNTS, rdict)
        print('caching rules_arrear_loans_total_counts are done.')

    def cache_rules_loan_monthly_installments_total_balance_ratios_v16(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V16_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, rdict)
        print('caching rules_loan_monthly_installments_total_balance_ratios are done.')

    def cache_rules_loans_total_counts_h11(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_TOTAL_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_TOTAL_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: H11_RULES_LOAN_TOTAL_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_TOTAL_COUNTS, rdict)
        print('caching rules_loans_total_counts are done.')

    def cache_rules_overdue_loans_total_balance_ratios_v18(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V18_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, rdict)
        print('caching rules_overdue_loans_total_balance_ratios are done.')

    def cache_rules_past_due_loans_total_balance_ratios_v19(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V19_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS, rdict)
        print('caching rules_past_due_loans_total_balance_ratios are done.')

    def cache_rules_past_due_loans_total_counts_t33(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_PAST_DUE_TOTAL_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T33_RULES_LOAN_PAST_DUE_TOTAL_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, rdict)
        print('caching rules_past_due_loans_total_counts are done.')

    def cache_rules_suspicious_loans_total_balance_ratios_v21(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: V21_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, rdict)
        print('caching rules_suspicious_loans_total_balance_ratios are done.')

    def cache_rules_suspicious_loans_total_counts_t35(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: T35_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS, rdict)
        print('caching rules_suspicious_loans_total_counts are done.')

    # ---------------------------- read cache methods ----------------------------------- #
    def get_score_of_rules_arrear_loans_total_balance_ratios_v20(self, arrear_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, arrear_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_arrear_loans_total_balance_ratios_v20(self, arrear_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, arrear_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_arrear_loans_total_counts_t34(self, arrear_loans_total_count):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_ARREAR_TOTAL_COUNTS, arrear_loans_total_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_arrear_loans_total_counts_t34(self, arrear_loans_total_count):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_ARREAR_TOTAL_COUNTS, arrear_loans_total_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_loan_monthly_installments_total_balance_ratios_v16(self, installments_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, installments_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_loan_monthly_installments_total_balance_ratios_v16(self, installments_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, installments_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_loans_total_counts_h11(self, loans_total_count):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_TOTAL_COUNTS, loans_total_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_loans_total_counts_h11(self, loans_total_count):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_TOTAL_COUNTS, loans_total_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_overdue_loans_total_balance_ratios_v18(self, overdue_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, overdue_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_overdue_loans_total_balance_ratios_v18(self, overdue_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, overdue_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_past_due_loans_total_balance_ratios_v19(self, past_due_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS, past_due_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_past_due_loans_total_balance_ratios_v19(self, past_due_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS, past_due_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_past_due_loans_total_counts_t33(self, past_due_loans_total_count):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, past_due_loans_total_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_past_due_loans_total_counts_t33(self, past_due_loans_total_count):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, past_due_loans_total_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_suspicious_loans_total_balance_ratios_v21(self, suspicious_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, suspicious_total_balance_ratio, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_suspicious_loans_total_balance_ratios_v21(self, suspicious_total_balance_ratio):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, suspicious_total_balance_ratio, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_suspicious_loans_total_counts_t35(self, suspicious_loans_total_count):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS, suspicious_loans_total_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_suspicious_loans_total_counts_t35(self, suspicious_loans_total_count):
        scores = self.rds.zrangebyscore(SET_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS, suspicious_loans_total_count, rules_max_val)
        return get_score_code_from_dict(scores)
