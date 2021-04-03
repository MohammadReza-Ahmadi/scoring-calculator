from redis import StrictRedis

from app.core.constants import rules_max_val, rules_min_val, \
    SET_RULES_PROFILE_HAS_KYCS, SET_RULES_PROFILE_ADDRESS_VERIFICATIONS, SET_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, \
    SET_RULES_PROFILE_MILITARY_SERVICE_STATUS, SET_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, SET_RULES_PROFILE_SIM_CARD_OWNERSHIPS, \
    SET_RULES_PROFILE_STAR_COUNTS_AVGS, I1_RULES_PROFILE_HAS_KYCS, H9_RULES_PROFILE_STAR_COUNTS_AVGS, I3_RULES_PROFILE_SIM_CARD_OWNERSHIPS, \
    H8_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, I2_RULES_PROFILE_MILITARY_SERVICE_STATUS, H5_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, \
    I4_RULES_PROFILE_ADDRESS_VERIFICATIONS, PARENT
from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum
from app.core.services.data_service import DataService
from app.core.services.util import get_score_from_dict, add_rule_to_dict, get_score_code_from_dict


# noinspection DuplicatedCode
class RedisCachingRulesProfiles:
    recreate_caches = True
    rds: StrictRedis = None
    ds: DataService = None

    def __init__(self, rds: StrictRedis, ds: DataService) -> None:
        self.rds = rds
        self.ds = ds

    def cache_rules(self):
        self.cache_rules_profile_has_kycs_i1()
        self.cache_rules_profile_address_verifications_i4()
        self.cache_rules_profile_membership_days_counts_h5()
        self.cache_rules_profile_military_service_status_i2()
        self.cache_rules_profile_recommended_to_others_counts_h8()
        self.cache_rules_profile_sim_card_ownerships_i3()
        self.cache_rules_profile_star_counts_avgs_h9()

    # ---------------------------- set cache methods ----------------------------------- #
    def cache_rules_profile_has_kycs_i1(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_PROFILE_HAS_KYCS)
        if not bool(self.rds.zcount(SET_RULES_PROFILE_HAS_KYCS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: I1_RULES_PROFILE_HAS_KYCS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_PROFILE_HAS_KYCS, rdict)
        print('caching rules_profile_has_kycs are done.')

    def cache_rules_profile_address_verifications_i4(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_PROFILE_ADDRESS_VERIFICATIONS)
        if not bool(self.rds.zcount(SET_RULES_PROFILE_ADDRESS_VERIFICATIONS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: I4_RULES_PROFILE_ADDRESS_VERIFICATIONS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_PROFILE_ADDRESS_VERIFICATIONS, rdict)
        print('caching rules_profile_address_verifications are done.')

    def cache_rules_profile_membership_days_counts_h5(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: H5_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, rdict)
        print('caching rules_profile_membership_days_counts are done.')

    def cache_rules_profile_military_service_status_i2(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_PROFILE_MILITARY_SERVICE_STATUS)
        if not bool(self.rds.zcount(SET_RULES_PROFILE_MILITARY_SERVICE_STATUS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: I2_RULES_PROFILE_MILITARY_SERVICE_STATUS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_PROFILE_MILITARY_SERVICE_STATUS, rdict)
        print('caching rules_profile_military_service_status are done.')

    def cache_rules_profile_recommended_to_others_counts_h8(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS)
        if not bool(self.rds.zcount(SET_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: H8_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, rdict)
        print('caching rules_profile_recommended_to_others_counts are done.')

    def cache_rules_profile_sim_card_ownerships_i3(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_PROFILE_SIM_CARD_OWNERSHIPS)
        if not bool(self.rds.zcount(SET_RULES_PROFILE_SIM_CARD_OWNERSHIPS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: I3_RULES_PROFILE_SIM_CARD_OWNERSHIPS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_PROFILE_SIM_CARD_OWNERSHIPS, rdict)
        print('caching rules_profile_sim_card_ownerships are done.')

    def cache_rules_profile_star_counts_avgs_h9(self):
        if self.recreate_caches:
            self.rds.delete(SET_RULES_PROFILE_STAR_COUNTS_AVGS)
        if not bool(self.rds.zcount(SET_RULES_PROFILE_STAR_COUNTS_AVGS, rules_min_val, rules_max_val)):
            rules: {} = self.ds.get_rules({PARENT: H9_RULES_PROFILE_STAR_COUNTS_AVGS})
            rdict = {}
            for r in rules:
                add_rule_to_dict(rdict, r)
            self.rds.zadd(SET_RULES_PROFILE_STAR_COUNTS_AVGS, rdict)
        print('caching rules_profile_star_counts_avgs are done.')

    # ---------------------------- read cache methods ----------------------------------- #
    def get_score_of_rules_profile_has_kycs_i1(self, has_kyc):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_HAS_KYCS, int(has_kyc), rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_profile_has_kycs_i1(self, has_kyc):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_HAS_KYCS, int(has_kyc), rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_profile_address_verifications_i4(self, address_verification):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_ADDRESS_VERIFICATIONS, int(address_verification), rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_profile_address_verifications_i4(self, address_verification):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_ADDRESS_VERIFICATIONS, int(address_verification), rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_profile_membership_days_counts_h5(self, membership_days_count):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, membership_days_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_profile_membership_days_counts_h5(self, membership_days_count):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, membership_days_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_profile_military_service_status_i2(self, military_service_status: ProfileMilitaryServiceStatusEnum):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_MILITARY_SERVICE_STATUS, military_service_status.value, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_profile_military_service_status_i2(self, military_service_status: ProfileMilitaryServiceStatusEnum):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_MILITARY_SERVICE_STATUS, military_service_status.value, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_profile_recommended_to_others_counts_h8(self, recommended_to_others_count):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, recommended_to_others_count, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_profile_recommended_to_others_counts_h8(self, recommended_to_others_count):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, recommended_to_others_count, rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_profile_sim_card_ownerships_i3(self, sim_card_ownership):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_SIM_CARD_OWNERSHIPS, int(sim_card_ownership), rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_profile_sim_card_ownerships_i3(self, sim_card_ownership):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_SIM_CARD_OWNERSHIPS, int(sim_card_ownership), rules_max_val)
        return get_score_code_from_dict(scores)

    def get_score_of_rules_profile_star_counts_avgs_h9(self, star_count_avg):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_STAR_COUNTS_AVGS, star_count_avg, rules_max_val)
        return get_score_from_dict(scores)

    def get_code_of_rules_profile_star_counts_avgs_h9(self, star_count_avg):
        scores = self.rds.zrangebyscore(SET_RULES_PROFILE_STAR_COUNTS_AVGS, star_count_avg, rules_max_val)
        return get_score_code_from_dict(scores)
