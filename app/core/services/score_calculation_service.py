from datetime import datetime

from numpy import long

from app.core.constants import SCORE_CODE_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, \
    SCORE_CODE_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, GENERAL_AVG_DEAL_AMOUNT, \
    GENERAL_AVG_DELAY_DAYS, \
    ALL_USERS_AVERAGE_UNFIXED_RETURNED_CHEQUES_AMOUNT, TIMELINESS_SCORE, IDENTITIES_SCORE, HISTORIES_SCORE, \
    VOLUMES_SCORE, NORMALIZATION_MAX_SCORE, ONE_HUNDRED, ALL_USERS_AVERAGE_MONTHLY_INSTALLMENT_AMOUNT, ZERO
from app.core.data.caching.redis_caching import RedisCaching
from app.core.data.caching.redis_caching_rules_cheques import RedisCachingRulesCheques
from app.core.data.caching.redis_caching_rules_done_trades import RedisCachingRulesDoneTrades
from app.core.data.caching.redis_caching_rules_loans import RedisCachingRulesLoans
from app.core.data.caching.redis_caching_rules_masters import RedisCachingRulesMasters
from app.core.data.caching.redis_caching_rules_profiles import RedisCachingRulesProfiles
from app.core.data.caching.redis_caching_rules_undone_trades import RedisCachingRulesUndoneTrades
from app.core.exceptions import ScoringException
from app.core.models.cheques import Cheque
from app.core.models.done_trades import DoneTrade
from app.core.models.loans import Loan
from app.core.models.profile import Profile
from app.core.models.score_changes import ScoreChange
from app.core.models.score_reasons import ScoreReason
from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum
from app.core.models.undone_trades import UndoneTrade
from app.core.services.data_service import DataService
from app.core.services.util import get_zero_if_none, create_new_score_change, is_none_or_zero_float, is_not_none
# noinspection DuplicatedCode
from app.core.settings import initial_score_change_store_config


# noinspection DuplicatedCode
class ScoreCalculationService:
    crm = None
    scores_dict = {
        IDENTITIES_SCORE: 0,
        HISTORIES_SCORE: 0,
        VOLUMES_SCORE: 0,
        TIMELINESS_SCORE: 0
    }

    def __init__(self, rds: RedisCaching, ds: DataService) -> None:
        self.rds = rds
        self.ds = ds
        self.crm = RedisCachingRulesMasters(rds.rds)

    def calculate_user_final_score(self, user_id: long):
        total_pure_score = self.calculate_user_profile_score(user_id)
        total_pure_score += self.calculate_user_done_trades_score(user_id)
        total_pure_score += self.calculate_user_undone_trades_score(user_id)
        total_pure_score += self.calculate_user_loans_score(user_id)
        total_pure_score += self.calculate_user_cheques_score(user_id)
        print('<><><><><><><> total_pure_score = {} <><><><><><><>'.format(total_pure_score))
        return total_pure_score

    # noinspection PyMethodMayBeStatic
    def validate_profile(self, p):
        if p is None:
            raise ScoringException(4, 'profile is none!')
        if p.user_id is None:
            raise ScoringException(1, 'user_id is none!')

    # noinspection DuplicatedCode
    def calculate_user_profile_score(self, recent_p: Profile = None, revised_p: Profile = None, reset_cache=False):
        self.validate_profile(revised_p)
        rds: RedisCachingRulesProfiles = self.rds.get_redis_caching_rules_profile_service(reset_cache)
        revised_p.last_score_change = ZERO
        profile_score = ZERO

        # self.initialize_revised_profile_scores(recent_p=recent_p, revised_p=p)
        # CALC ADDRESS_VERIFICATION'S SCORE
        revised_rule_score = rds.get_score_of_rules_profile_address_verifications_i4(revised_p.address_verification)
        # handle score change reason
        rule_code = rds.get_code_of_rules_profile_address_verifications_i4(revised_p.address_verification)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_p.address_verification_score, revised_rule_score)
        # update score values in related entity
        revised_p.identities_score += score_change
        revised_p.address_verification_score = revised_rule_score
        profile_score += revised_rule_score
        print('score= {}, profile:[address_verification-i4]= {}'.format(revised_rule_score, revised_p.address_verification))

        # CALC HAS_KYC'S SCORE
        revised_rule_score = rds.get_score_of_rules_profile_has_kycs_i1(revised_p.has_kyc)
        # handle score change reason
        rule_code = rds.get_code_of_rules_profile_has_kycs_i1(revised_p.has_kyc)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_p.has_kyc_score, revised_rule_score)
        # update score values in related entity
        revised_p.identities_score += score_change
        revised_p.has_kyc_score = revised_rule_score
        profile_score += revised_rule_score
        print('score= {}, profile:[has_kyc-i1]= {}'.format(revised_rule_score, revised_p.has_kyc))

        # CALC MEMBERSHIP_DAYS_COUNT'S SCORE
        # calculate membership days count
        member_ship_days_count = (datetime.today().date() - revised_p.membership_date).days if is_not_none(revised_p.membership_date) else ZERO
        revised_rule_score = rds.get_score_of_rules_profile_membership_days_counts_h5(member_ship_days_count)
        # handle score change reason
        rule_code = rds.get_code_of_rules_profile_membership_days_counts_h5(member_ship_days_count)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_p.membership_date_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_p.membership_date_score = revised_rule_score
        profile_score += revised_rule_score
        print('score= {}, profile:[membership_date-h5]= {}, profile_member_ship_days_count={}'.format(revised_rule_score, revised_p.membership_date, member_ship_days_count))

        # CALC MILITARY_SERVICE_STATUS'S SCORE
        if revised_p.military_service_status != ProfileMilitaryServiceStatusEnum.UNKNOWN:
            revised_rule_score = rds.get_score_of_rules_profile_military_service_status_i2(revised_p.military_service_status)
            # handle score change reason
            rule_code = rds.get_code_of_rules_profile_military_service_status_i2(revised_p.military_service_status)
        else:
            revised_rule_score = ZERO
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_p.military_service_status_score, revised_rule_score)
        # update score values in related entity
        revised_p.identities_score += score_change
        revised_p.military_service_status_score = revised_rule_score
        profile_score += revised_rule_score
        print('score= {}, profile:[military_service_status-i2]= {}'.format(revised_rule_score, revised_p.military_service_status))

        # CALC RECOMMENDED_TO_OTHERS' SCORE
        revised_rule_score = rds.get_score_of_rules_profile_recommended_to_others_counts_h8(get_zero_if_none(revised_p.recommended_to_others_count))
        # handle score change reason
        rule_code = rds.get_code_of_rules_profile_recommended_to_others_counts_h8(get_zero_if_none(revised_p.recommended_to_others_count))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_p.recommended_to_others_count_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_p.recommended_to_others_count_score = revised_rule_score
        profile_score += revised_rule_score
        print('score= {}, profile:[recommended_to_others_count-h8]= {}'.format(revised_rule_score, get_zero_if_none(revised_p.recommended_to_others_count)))

        # CALC SIM_CARD_OWNERSHIP'S SCORE
        revised_rule_score = rds.get_score_of_rules_profile_sim_card_ownerships_i3(revised_p.sim_card_ownership)
        # handle score change reason
        rule_code = rds.get_code_of_rules_profile_sim_card_ownerships_i3(revised_p.sim_card_ownership)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_p.sim_card_ownership_score, revised_rule_score)
        # update score values in related entity
        revised_p.identities_score += score_change
        revised_p.sim_card_ownership_score = revised_rule_score
        profile_score += revised_rule_score
        print('score= {}, profile:[sim_card_ownership-i3]= {}'.format(revised_rule_score, revised_p.sim_card_ownership))

        # CALC STAR_COUNT'S SCORE
        revised_rule_score = rds.get_score_of_rules_profile_star_counts_avgs_h9(get_zero_if_none(revised_p.star_count_average))
        # handle score change reason
        rule_code = rds.get_code_of_rules_profile_star_counts_avgs_h9(get_zero_if_none(revised_p.star_count_average))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_p.star_count_average_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_p.star_count_average_score = revised_rule_score
        profile_score += revised_rule_score
        print('score= {}, profile:[star_count_average-h9]= {}'.format(revised_rule_score, revised_p.star_count_average))

        print('............. profile score = {} ................'.format(profile_score))
        self.print_score(revised_p)
        return profile_score

    def calculate_user_done_trades_score(self, revised_p: Profile = None, reset_cache=False, recent_dt: DoneTrade = None, revised_dt: DoneTrade = None):
        self.validate_profile(revised_p)
        rds: RedisCachingRulesDoneTrades = self.rds.get_redis_caching_rules_done_trades_service(reset_cache)
        done_trades_score = 0

        revised_rule_score = rds.get_score_of_rules_done_timely_trades_of_last_3_months_h6(get_zero_if_none(revised_dt.timely_trades_count_of_last_3_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_done_timely_trades_of_last_3_months_h6(get_zero_if_none(revised_dt.timely_trades_count_of_last_3_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_dt.timely_trades_count_of_last_3_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_dt.timely_trades_count_of_last_3_months_score = revised_rule_score
        done_trades_score += revised_rule_score
        print('score= {}, doneTrades:[timely_trades_count_of_last_3_months_h6]= {}'.format(revised_rule_score, revised_dt.timely_trades_count_of_last_3_months))

        revised_rule_score = rds.get_score_of_rules_done_timely_trades_between_last_3_to_12_months_h7(get_zero_if_none(revised_dt.timely_trades_count_between_last_3_to_12_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_done_timely_trades_between_last_3_to_12_months_h7(get_zero_if_none(revised_dt.timely_trades_count_between_last_3_to_12_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_dt.timely_trades_count_between_last_3_to_12_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_dt.timely_trades_count_between_last_3_to_12_months_score = revised_rule_score
        done_trades_score += revised_rule_score
        print('score= {}, doneTrades:[timely_trades_count_between_last_3_to_12_months-h7]= {}'.format(revised_rule_score, revised_dt.timely_trades_count_between_last_3_to_12_months))

        revised_rule_score = rds.get_score_of_rules_done_past_due_trades_of_last_3_months_t22(get_zero_if_none(revised_dt.past_due_trades_count_of_last_3_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_done_past_due_trades_of_last_3_months_t22(get_zero_if_none(revised_dt.past_due_trades_count_of_last_3_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_dt.past_due_trades_count_of_last_3_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_dt.past_due_trades_count_of_last_3_months_score = revised_rule_score
        done_trades_score += revised_rule_score
        print('score= {}, doneTrades:[past_due_trades_count_of_last_3_months-t22]= {}'.format(revised_rule_score, revised_dt.past_due_trades_count_of_last_3_months))

        revised_rule_score = rds.get_score_of_rules_done_past_due_trades_between_last_3_to_12_months_t23(get_zero_if_none(revised_dt.past_due_trades_count_between_last_3_to_12_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_done_past_due_trades_between_last_3_to_12_months_t23(get_zero_if_none(revised_dt.past_due_trades_count_between_last_3_to_12_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_dt.past_due_trades_count_between_last_3_to_12_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_dt.past_due_trades_count_between_last_3_to_12_months_score = revised_rule_score
        done_trades_score += revised_rule_score
        print('score= {}, doneTrades:[past_due_trades_count_between_last_3_to_12_months-t23]= {}'.format(revised_rule_score, revised_dt.past_due_trades_count_between_last_3_to_12_months))

        revised_rule_score = rds.get_score_of_rules_done_arrear_trades_of_last_3_months_t24(get_zero_if_none(revised_dt.arrear_trades_count_of_last_3_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_done_arrear_trades_of_last_3_months_t24(get_zero_if_none(revised_dt.arrear_trades_count_of_last_3_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_dt.arrear_trades_count_of_last_3_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_dt.arrear_trades_count_of_last_3_months_score = revised_rule_score
        done_trades_score += revised_rule_score
        print('score= {}, doneTrades:[arrear_trades_count_of_last_3_months-t24]= {}'.format(revised_rule_score, revised_dt.arrear_trades_count_of_last_3_months))

        revised_rule_score = rds.get_score_of_rules_done_arrear_trades_between_last_3_to_12_months_t25(get_zero_if_none(revised_dt.arrear_trades_count_between_last_3_to_12_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_done_arrear_trades_between_last_3_to_12_months_t25(get_zero_if_none(revised_dt.arrear_trades_count_between_last_3_to_12_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_dt.arrear_trades_count_between_last_3_to_12_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_dt.arrear_trades_count_between_last_3_to_12_months_score = revised_rule_score
        done_trades_score += revised_rule_score
        print('score= {}, doneTrades:[arrear_trades_count_between_last_3_to_12_months-t25]= {}'.format(revised_rule_score, revised_dt.arrear_trades_count_between_last_3_to_12_months))

        # calculate average of total balance
        # todo: should calculate all users' trades total balance
        avg_total_balance_ratio = 0 if is_none_or_zero_float(revised_dt.trades_total_balance) or GENERAL_AVG_DEAL_AMOUNT == 0 else revised_dt.trades_total_balance / GENERAL_AVG_DEAL_AMOUNT
        avg_total_balance_ratio = float(avg_total_balance_ratio)
        revised_rule_score = rds.get_score_of_rules_done_trades_average_total_balance_ratios_v12(avg_total_balance_ratio)
        # handle score change reason
        rule_code = rds.get_code_of_rules_done_trades_average_total_balance_ratios_v12(avg_total_balance_ratio)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_dt.average_total_balance_ratios_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_dt.average_total_balance_ratios_score = revised_rule_score
        done_trades_score += revised_rule_score
        print('score= {}, doneTrades:[avg_total_balance-v12]= {}'.format(revised_rule_score, avg_total_balance_ratio))

        # calculate average of all users delay days
        # todo: should calculate all users' average of done trades delay days (general_avg_delay_days)
        # general_avg_delay_days = 0
        avg_delay_days = 0 if GENERAL_AVG_DELAY_DAYS == 0 else int(get_zero_if_none(revised_dt.total_delay_days)) / GENERAL_AVG_DELAY_DAYS
        revised_rule_score = rds.get_score_of_rules_done_trades_average_delay_days_t28(avg_delay_days)
        # handle score change reason
        rule_code = rds.get_code_of_rules_done_trades_average_delay_days_t28(avg_delay_days)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_dt.average_delay_days_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_dt.average_delay_days_score = revised_rule_score
        done_trades_score += revised_rule_score
        print('score= {}, doneTrades:[avg_delay_days-t28]= {}'.format(revised_rule_score, revised_dt.total_delay_days))

        print('............. doneTrades score = {} ................'.format(done_trades_score))
        self.print_score(revised_p)
        return done_trades_score

    def calculate_user_undone_trades_score(self, revised_p: Profile = None, reset_cache=False, recent_udt: UndoneTrade = None, revised_udt: UndoneTrade = None, dt: DoneTrade = None):
        self.validate_profile(revised_p)
        rds: RedisCachingRulesUndoneTrades = self.rds.get_redis_caching_rules_undone_trades_service(reset_cache)
        undone_trades_score = 0

        revised_rule_score = rds.get_score_of_rules_undone_undue_trades_counts_h10(get_zero_if_none(revised_udt.undue_trades_count))
        # handle score change reason
        rule_code = rds.get_code_of_rules_undone_undue_trades_counts_h10(get_zero_if_none(revised_udt.undue_trades_count))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_udt.undue_trades_count_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_udt.undue_trades_count_score = revised_rule_score
        undone_trades_score += revised_rule_score
        print('score= {}, undoneTrades:[undue_trades_count-h10]= {}'.format(revised_rule_score, revised_udt.undue_trades_count))

        undue_total_balance_ratio = float(get_zero_if_none(revised_udt.undue_trades_total_balance_of_last_year) / dt.trades_total_balance) if is_not_none(dt.trades_total_balance) else ZERO
        revised_rule_score = rds.get_score_of_rules_undone_undue_trades_total_balance_of_last_year_ratios_v15(undue_total_balance_ratio)
        # handle score change reason
        rule_code = rds.get_code_of_rules_undone_undue_trades_total_balance_of_last_year_ratios_v15(undue_total_balance_ratio)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_udt.undue_trades_total_balance_of_last_year_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_udt.undue_trades_total_balance_of_last_year_score = revised_rule_score
        undone_trades_score += revised_rule_score
        print('score= {}, undoneTrades:[undue_total_balance_ratio-v15]= {}'.format(revised_rule_score, undue_total_balance_ratio))

        revised_rule_score = rds.get_score_of_rules_undone_past_due_trades_counts_t26(get_zero_if_none(revised_udt.past_due_trades_count))
        # handle score change reason
        rule_code = rds.get_code_of_rules_undone_past_due_trades_counts_t26(get_zero_if_none(revised_udt.past_due_trades_count))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_udt.past_due_trades_count_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_udt.past_due_trades_count_score = revised_rule_score
        undone_trades_score += revised_rule_score
        print('score= {}, undoneTrades:[past_due_trades_count-t26]= {}'.format(revised_rule_score, revised_udt.past_due_trades_count))

        timely_done_trades_of_last_year = (get_zero_if_none(dt.timely_trades_count_of_last_3_months) + get_zero_if_none(dt.timely_trades_count_between_last_3_to_12_months))
        # calculate past_due_total_balance_ratio
        if is_none_or_zero_float(revised_udt.past_due_trades_total_balance_of_last_year) or is_none_or_zero_float(dt.trades_total_balance):
            past_due_total_balance_ratio = 0
        else:
            past_due_total_balance_ratio = float(revised_udt.past_due_trades_total_balance_of_last_year / dt.trades_total_balance)
        revised_rule_score = rds.get_score_of_rules_undone_past_due_trades_total_balance_of_last_year_ratios_v13(past_due_total_balance_ratio)
        rule_code = rds.get_code_of_rules_undone_past_due_trades_total_balance_of_last_year_ratios_v13(past_due_total_balance_ratio)
        if timely_done_trades_of_last_year == 1 and rule_code == SCORE_CODE_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS:
            revised_rule_score *= 2
        # handle score change reason
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_udt.past_due_trades_total_balance_of_last_year_score, revised_rule_score)
        # update score values in related entity
        revised_p.volumes_score += score_change
        revised_udt.past_due_trades_total_balance_of_last_year_score = revised_rule_score
        undone_trades_score += revised_rule_score
        print('score= {}, undoneTrades:[past_due_total_balance_ratio-v13]= {}'.format(revised_rule_score, past_due_total_balance_ratio))

        revised_rule_score = rds.get_score_of_rules_undone_arrear_trades_counts_t27(get_zero_if_none(revised_udt.arrear_trades_count))
        # handle score change reason
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_udt.arrear_trades_count_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_udt.arrear_trades_count_score = revised_rule_score
        undone_trades_score += revised_rule_score
        print('score= {}, undoneTrades:[arrear_trades_count-t27]= {}'.format(revised_rule_score, revised_udt.arrear_trades_count))

        # calculate arrear_total_balance_ratio
        arrear_total_balance_ratio = ZERO if is_none_or_zero_float(dt.trades_total_balance) else float(get_zero_if_none(revised_udt.arrear_trades_total_balance_of_last_year) / dt.trades_total_balance)
        revised_rule_score = rds.get_score_of_rules_undone_arrear_trades_total_balance_of_last_year_ratios_v14(arrear_total_balance_ratio)
        rule_code = rds.get_code_of_rules_undone_arrear_trades_total_balance_of_last_year_ratios_v14(arrear_total_balance_ratio)
        if timely_done_trades_of_last_year == 1 and rule_code == SCORE_CODE_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS:
            revised_rule_score *= 2
        # handle score change reason
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_udt.arrear_trades_total_balance_of_last_year_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_udt.arrear_trades_total_balance_of_last_year_score = revised_rule_score
        undone_trades_score += revised_rule_score
        print('score= {}, undoneTrades:[arrear_total_balance_ratio-v14]= {}'.format(revised_rule_score, arrear_total_balance_ratio))

        print('............. undoneTrades_score = {} ................'.format(undone_trades_score))
        self.print_score(revised_p)
        return undone_trades_score

    def calculate_user_loans_score(self, revised_p: Profile = None, reset_cache=False, recent_ln: Loan = None, revised_ln: Loan = None):
        self.validate_profile(revised_p)
        rds: RedisCachingRulesLoans = self.rds.get_redis_caching_rules_loans_service(reset_cache)
        loans_score = 0

        revised_rule_score = rds.get_score_of_rules_loans_total_counts_h11(get_zero_if_none(revised_ln.loans_total_count))
        # handle score change reason
        rule_code = rds.get_code_of_rules_loans_total_counts_h11(get_zero_if_none(revised_ln.loans_total_count))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.loans_total_count_score, revised_rule_score)
        # update score values in related entity
        revised_p.histories_score += score_change
        revised_ln.loans_total_count_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[loans_total_count-h11]= {}'.format(revised_rule_score, revised_ln.loans_total_count))

        # should be calculate avg_of_all_users_monthly_installment_total_balance
        installments_total_balance_ratio = 0 if ALL_USERS_AVERAGE_MONTHLY_INSTALLMENT_AMOUNT == 0 else float(get_zero_if_none(revised_ln.monthly_installments_total_balance) / ALL_USERS_AVERAGE_MONTHLY_INSTALLMENT_AMOUNT)
        revised_rule_score = rds.get_score_of_rules_loan_monthly_installments_total_balance_ratios_v16(installments_total_balance_ratio)
        # handle score change reason
        rule_code = rds.get_code_of_rules_loan_monthly_installments_total_balance_ratios_v16(installments_total_balance_ratio)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.monthly_installments_total_balance_score, revised_rule_score)
        # update score values in related entity
        revised_p.volumes_score += score_change
        revised_ln.monthly_installments_total_balance_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[installments_total_balance_ratio-v16]= {}'.format(revised_rule_score, installments_total_balance_ratio))

        # should be calculate user_total_loans_balance
        overdue_total_balance_ratio = ZERO if revised_ln.loans_total_balance == 0 else float(get_zero_if_none(revised_ln.overdue_loans_total_balance) / revised_ln.loans_total_balance)
        revised_rule_score = rds.get_score_of_rules_overdue_loans_total_balance_ratios_v18(overdue_total_balance_ratio)
        # handle score change reason
        rule_code = rds.get_code_of_rules_overdue_loans_total_balance_ratios_v18(overdue_total_balance_ratio)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.overdue_loans_total_balance_score, revised_rule_score)
        # update score values in related entity
        revised_p.volumes_score += score_change
        revised_ln.overdue_loans_total_balance_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[overdue_total_balance_ratio-v18]= {}'.format(revised_rule_score, overdue_total_balance_ratio))

        revised_rule_score = rds.get_score_of_rules_past_due_loans_total_counts_t33(get_zero_if_none(revised_ln.past_due_loans_total_count))
        # handle score change reason
        rule_code = rds.get_code_of_rules_past_due_loans_total_counts_t33(get_zero_if_none(revised_ln.past_due_loans_total_count))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.past_due_loans_total_count_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_ln.past_due_loans_total_count_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[past_due_loans_total_count-t33]= {}'.format(revised_rule_score, revised_ln.past_due_loans_total_count))

        # should be calculate user_total_loans_balance
        past_due_total_balance_ratio = 0 if revised_ln.loans_total_balance == 0 else float(get_zero_if_none(revised_ln.past_due_loans_total_balance) / revised_ln.loans_total_balance)
        revised_rule_score = rds.get_score_of_rules_past_due_loans_total_balance_ratios_v19(past_due_total_balance_ratio)
        # handle score change reason
        rule_code = rds.get_code_of_rules_past_due_loans_total_balance_ratios_v19(past_due_total_balance_ratio)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.past_due_loans_total_balance_score, revised_rule_score)
        # update score values in related entity
        revised_p.volumes_score += score_change
        revised_ln.past_due_loans_total_balance_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[past_due_total_balance_ratio-v19]= {}'.format(revised_rule_score, past_due_total_balance_ratio))

        revised_rule_score = rds.get_score_of_rules_arrear_loans_total_counts_t34(get_zero_if_none(revised_ln.arrear_loans_total_count))
        # handle score change reason
        rule_code = rds.get_code_of_rules_arrear_loans_total_counts_t34(get_zero_if_none(revised_ln.arrear_loans_total_count))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.arrear_loans_total_count_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_ln.arrear_loans_total_count_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[arrear_loans_total_count-t34]= {}'.format(revised_rule_score, revised_ln.arrear_loans_total_count))

        # should be calculate user_total_loans_balance
        arrear_total_balance_ratio = 0 if revised_ln.loans_total_balance == 0 else float(get_zero_if_none(revised_ln.arrear_loans_total_balance) / revised_ln.loans_total_balance)
        revised_rule_score = rds.get_score_of_rules_arrear_loans_total_balance_ratios_v20(arrear_total_balance_ratio)
        # handle score change reason
        rule_code = rds.get_code_of_rules_arrear_loans_total_balance_ratios_v20(arrear_total_balance_ratio)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.arrear_loans_total_balance_score, revised_rule_score)
        # update score values in related entity
        revised_p.volumes_score += score_change
        revised_ln.arrear_loans_total_balance_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[arrear_total_balance_ratio-v20]= {}'.format(revised_rule_score, arrear_total_balance_ratio))

        revised_rule_score = rds.get_score_of_rules_suspicious_loans_total_counts_t35(get_zero_if_none(revised_ln.suspicious_loans_total_count))
        # handle score change reason
        rule_code = rds.get_code_of_rules_suspicious_loans_total_counts_t35(get_zero_if_none(revised_ln.suspicious_loans_total_count))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.suspicious_loans_total_count_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_ln.suspicious_loans_total_count_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[suspicious_loans_total_count-t35]= {}'.format(revised_rule_score, revised_ln.suspicious_loans_total_count))

        # should be calculate user_total_loans_balance
        if is_none_or_zero_float(revised_ln.suspicious_loans_total_balance) | is_none_or_zero_float(revised_ln.loans_total_balance):
            suspicious_total_balance_ratio = 0
        else:
            suspicious_total_balance_ratio = float(revised_ln.suspicious_loans_total_balance / revised_ln.loans_total_balance)
        revised_rule_score = rds.get_score_of_rules_suspicious_loans_total_balance_ratios_v21(suspicious_total_balance_ratio)
        # handle score change reason
        rule_code = rds.get_code_of_rules_suspicious_loans_total_balance_ratios_v21(suspicious_total_balance_ratio)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ln.suspicious_loans_total_balance_score, revised_rule_score)
        # update score values in related entity
        revised_p.volumes_score += score_change
        revised_ln.suspicious_loans_total_balance_score = revised_rule_score
        loans_score += revised_rule_score
        print('score= {}, loans:[suspicious_total_balance_ratio-v21]= {}'.format(revised_rule_score, suspicious_total_balance_ratio))

        print('............. loans_score = {} ................'.format(loans_score))
        self.print_score(revised_p)
        return loans_score

    def calculate_user_cheques_score(self, revised_p: Profile = None, reset_cache=False, recent_ch: Cheque = None, revised_ch: Cheque = None):
        self.validate_profile(revised_p)
        rds: RedisCachingRulesCheques = self.rds.get_redis_caching_rules_cheques_service(reset_cache)
        cheques_score = 0

        revised_rule_score = rds.get_score_of_rules_unfixed_returned_cheques_count_between_last_3_to_12_months_t30(get_zero_if_none(revised_ch.unfixed_returned_cheques_count_between_last_3_to_12_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_unfixed_returned_cheques_count_between_last_3_to_12_months_t30(get_zero_if_none(revised_ch.unfixed_returned_cheques_count_between_last_3_to_12_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ch.unfixed_returned_cheques_count_between_last_3_to_12_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_ch.unfixed_returned_cheques_count_between_last_3_to_12_months_score = revised_rule_score
        cheques_score += revised_rule_score
        print('score= {}, cheques:[unfixed_returned_cheques_count_between_last_3_to_12_months-t30]= {}'.format(revised_rule_score, revised_ch.unfixed_returned_cheques_count_between_last_3_to_12_months))

        revised_rule_score = rds.get_score_of_rules_unfixed_returned_cheques_count_of_last_3_months_t29(get_zero_if_none(revised_ch.unfixed_returned_cheques_count_of_last_3_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_unfixed_returned_cheques_count_of_last_3_months_t29(get_zero_if_none(revised_ch.unfixed_returned_cheques_count_of_last_3_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ch.unfixed_returned_cheques_count_of_last_3_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_ch.unfixed_returned_cheques_count_of_last_3_months_score = revised_rule_score
        cheques_score += revised_rule_score
        print('score= {}, cheques:[unfixed_returned_cheques_count_of_last_3_months-t29]= {}'.format(revised_rule_score, revised_ch.unfixed_returned_cheques_count_of_last_3_months))

        revised_rule_score = rds.get_score_of_rules_unfixed_returned_cheques_count_of_last_5_years_t32(get_zero_if_none(revised_ch.unfixed_returned_cheques_count_of_last_5_years))
        # handle score change reason
        rule_code = rds.get_code_of_rules_unfixed_returned_cheques_count_of_last_5_years_t32(get_zero_if_none(revised_ch.unfixed_returned_cheques_count_of_last_5_years))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ch.unfixed_returned_cheques_count_of_last_5_years_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_ch.unfixed_returned_cheques_count_of_last_5_years_score = revised_rule_score
        cheques_score += revised_rule_score
        print('score= {}, cheques:[unfixed_returned_cheques_count_of_last_5_years-t32]= {}'.format(revised_rule_score, revised_ch.unfixed_returned_cheques_count_of_last_5_years))

        revised_rule_score = rds.get_score_of_rules_unfixed_returned_cheques_count_of_more_12_months_t31(get_zero_if_none(revised_ch.unfixed_returned_cheques_count_of_more_12_months))
        # handle score change reason
        rule_code = rds.get_code_of_rules_unfixed_returned_cheques_count_of_more_12_months_t31(get_zero_if_none(revised_ch.unfixed_returned_cheques_count_of_more_12_months))
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ch.unfixed_returned_cheques_count_of_more_12_months_score, revised_rule_score)
        # update score values in related entity
        revised_p.timeliness_score += score_change
        revised_ch.unfixed_returned_cheques_count_of_more_12_months_score = revised_rule_score
        cheques_score += revised_rule_score
        print('score= {}, cheques:[unfixed_returned_cheques_count_of_more_12_months]-t31= {}'.format(revised_rule_score, revised_ch.unfixed_returned_cheques_count_of_more_12_months))

        # should be calculate avg_of_all_users_unfixed_returned_cheques_total_balance
        total_balance_ratio = float(get_zero_if_none(revised_ch.unfixed_returned_cheques_total_balance) / ALL_USERS_AVERAGE_UNFIXED_RETURNED_CHEQUES_AMOUNT)
        revised_rule_score = rds.get_score_of_rules_unfixed_returned_cheques_total_balance_ratios_v17(total_balance_ratio)
        # handle score change reason
        rule_code = rds.get_code_of_rules_unfixed_returned_cheques_total_balance_ratios_v17(total_balance_ratio)
        score_change = self.resolve_and_save_score_change(revised_p, rule_code, recent_ch.unfixed_returned_cheques_total_balance_score, revised_rule_score)
        # update score values in related entity
        revised_p.volumes_score += score_change
        revised_ch.unfixed_returned_cheques_total_balance_score = revised_rule_score
        cheques_score += revised_rule_score
        print('score= {}, cheques:[total_balance_ratio-v17]= {}'.format(revised_rule_score, total_balance_ratio))

        print('............. cheques score = {} ................'.format(cheques_score))
        self.print_score(revised_p)
        return cheques_score

    # normalized score section --------------------------------------------
    def calculate_identities_normalized_score(self, identities_pure_score: int):
        # get all groups max score from redis
        identities_max_percent = float(self.crm.get_impact_percent_of_rule_identities_master())
        identities_max_score = float(self.crm.get_score_of_rule_identities_master())
        identities_normalized_score = round(
            ((identities_pure_score / identities_max_score) * NORMALIZATION_MAX_SCORE) * (
                    identities_max_percent / ONE_HUNDRED))
        print(
            '... identities_max_percent= {}, identities_max_score= {}, identities_pure_score= {}, identities_normalized_score= {}'
                .format(identities_max_percent, identities_max_score, identities_pure_score,
                        identities_normalized_score))
        return identities_normalized_score

    def calculate_histories_normalized_score(self, histories_pure_score: int):
        histories_max_score = float(self.crm.get_score_of_rule_histories_master())
        histories_max_percent = float(self.crm.get_impact_percent_of_rule_histories_master())
        histories_normalized_score = round(
            ((histories_pure_score / histories_max_score) * NORMALIZATION_MAX_SCORE) * (
                    histories_max_percent / ONE_HUNDRED))
        print(
            '... histories_max_percent= {}, histories_max_score= {}, histories_pure_score= {}, histories_normalized_score= {}'
                .format(histories_max_percent, histories_max_score, histories_pure_score, histories_normalized_score))
        return histories_normalized_score

    def calculate_volumes_normalized_score(self, volumes_pure_score: int):
        volumes_max_score = float(self.crm.get_score_of_rule_volumes_master())
        volumes_max_percent = float(self.crm.get_impact_percent_of_rule_volumes_master())
        volumes_normalized_score = round(
            ((volumes_pure_score / volumes_max_score) * NORMALIZATION_MAX_SCORE) * (volumes_max_percent / ONE_HUNDRED))
        print('... volumes_max_percent= {}, volumes_max_score= {}, volumes_pure_score= {}, volumes_normalized_score= {}'
              .format(volumes_max_percent, volumes_max_score, volumes_pure_score, volumes_normalized_score))
        return volumes_normalized_score

    def calculate_timeliness_normalized_score(self, timeliness_pure_score: int):
        timeliness_max_score = float(self.crm.get_score_of_rule_timeliness_master())
        timeliness_max_percent = float(self.crm.get_impact_percent_of_rule_timeliness_master())
        timeliness_normalized_score = round(
            ((timeliness_pure_score / timeliness_max_score) * NORMALIZATION_MAX_SCORE) * (
                    timeliness_max_percent / ONE_HUNDRED))
        print('... timeliness_max_percent= {}, timeliness_max_score= {}, timeliness_pure_score= {}, timeliness_normalized_score= {}'.format(timeliness_max_percent, timeliness_max_score, timeliness_pure_score, timeliness_normalized_score))
        return timeliness_normalized_score

    def resolve_and_save_score_change(self, profile: Profile, rule_code: str, recent_rule_score: int, revised_rule_score: int):
        if not initial_score_change_store_config and recent_rule_score is None:
            print('----------------------------------------- filed is None !!!!!!!!!!!!!!!!!')
            profile.score += revised_rule_score
            profile.last_score_change += revised_rule_score
            return revised_rule_score
        if revised_rule_score == recent_rule_score:
            return ZERO
        rs: ScoreReason = self.ds.get_score_reason_by_rule_code(rule_code)
        score_change = revised_rule_score - recent_rule_score
        profile.score += score_change
        profile.last_score_change += score_change
        ch: ScoreChange = create_new_score_change(profile.user_id, rule_code, score_change, profile.score)
        if revised_rule_score > recent_rule_score:
            ch.reason_desc = rs.positive_reason
        else:
            ch.reason_desc = rs.negative_reason
        self.ds.insert_score_change(ch)
        return score_change

    # noinspection PyMethodMayBeStatic
    def initialize_revised_profile_scores(self, recent_p: Profile, revised_p: Profile):
        revised_p.score = recent_p.score
        revised_p.identities_score = recent_p.identities_score
        revised_p.histories_score = recent_p.histories_score
        revised_p.timeliness_score = recent_p.timeliness_score
        revised_p.volumes_score = recent_p.volumes_score

    # noinspection PyMethodMayBeStatic
    def print_score(self, p):
        print('... SCORE={} [IDENTITIES_SCORE= {} , HISTORIES_SCORE= {}, VOLUMES_SCORE= {}, TIMELINESS_SCORE= {}] \n'.format(p.score, p.identities_score, p.histories_score, p.volumes_score, p.timeliness_score))
