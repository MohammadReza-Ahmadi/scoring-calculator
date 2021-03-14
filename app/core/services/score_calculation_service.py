from datetime import date

from numpy import long

from app.core.constants import SCORE_CODE_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, \
    SCORE_CODE_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, GENERAL_AVG_DEAL_AMOUNT, \
    GENERAL_AVG_DELAY_DAYS, \
    ALL_USERS_AVERAGE_UNFIXED_RETURNED_CHEQUES_AMOUNT, TIMELINESS_SCORE, IDENTITIES_SCORE, HISTORIES_SCORE, \
    VOLUMES_SCORE, NORMALIZATION_MAX_SCORE, ONE_HUNDRED, ALL_USERS_AVERAGE_MONTHLY_INSTALLMENT_AMOUNT
from app.core.data.caching.redis_caching import RedisCaching
from app.core.data.caching.redis_caching_rules_cheques import RedisCachingRulesCheques
from app.core.data.caching.redis_caching_rules_done_trades import RedisCachingRulesDoneTrades
from app.core.data.caching.redis_caching_rules_loans import RedisCachingRulesLoans
from app.core.data.caching.redis_caching_rules_masters import RedisCachingRulesMasters
from app.core.data.caching.redis_caching_rules_profiles import RedisCachingRulesProfiles
from app.core.data.caching.redis_caching_rules_undone_trades import RedisCachingRulesUndoneTrades
from app.core.models.cheques import Cheque
from app.core.models.done_trades import DoneTrade
from app.core.models.loans import Loan
from app.core.models.profile import Profile
from app.core.models.undone_trades import UndoneTrade
from app.core.services.data_service import DataService


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

    def calculate_user_profile_score(self, user_id: long, reset_cache=False, profile_object: Profile = None):
        profile: Profile
        if profile_object is not None:
            profile = profile_object
        else:
            # profile = Profile.objects(user_id=user_id).first()
            profile = self.ds.get_user_profile(user_id)

        rds: RedisCachingRulesProfiles = self.rds.get_redis_caching_rules_profile_service(reset_cache)
        profile_score = 0
        normalized_profile_score = 0

        score = rds.get_score_of_rules_profile_address_verifications_i4(profile.address_verification)
        # normalized_score = calculate_normalized_score(I4_RULES_PROFILE_ADDRESS_VERIFICATIONS, score)
        # normalized_profile_score += normalized_score
        profile_score += score
        self.scores_dict[IDENTITIES_SCORE] = self.scores_dict.get(IDENTITIES_SCORE) + score
        print('score= {}, profile:[address_verification-i4]= {}'.format(score, profile.address_verification))

        score = rds.get_score_of_rules_profile_has_kycs_i1(profile.has_kyc)
        # normalized_score = calculate_normalized_score(I1_RULES_PROFILE_HAS_KYCS, score)
        # normalized_profile_score += normalized_score
        profile_score += score
        self.scores_dict[IDENTITIES_SCORE] = self.scores_dict.get(IDENTITIES_SCORE) + score
        print('score= {}, profile:[has_kyc-i1]= {}'.format(score, profile.has_kyc))

        # calculate membership days count
        member_ship_days_count = (date.today() - profile.membership_date).days
        score = rds.get_score_of_rules_profile_membership_days_counts_h5(member_ship_days_count)
        # normalized_score = calculate_normalized_score(H5_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, score)
        # normalized_profile_score += normalized_score
        profile_score += score
        self.scores_dict[HISTORIES_SCORE] = self.scores_dict.get(HISTORIES_SCORE) + score
        print('score= {}, profile:[membership_date-h5]= {}, profile_member_ship_days_count={}'.format(score,
                                                                                                      profile.membership_date,
                                                                                                      member_ship_days_count))
        score = rds.get_score_of_rules_profile_military_service_status_i2(profile.military_service_status)
        # normalized_score = calculate_normalized_score(I2_RULES_PROFILE_MILITARY_SERVICE_STATUS, score)
        # normalized_profile_score += normalized_score
        profile_score += score
        self.scores_dict[IDENTITIES_SCORE] = self.scores_dict.get(IDENTITIES_SCORE) + score
        print('score= {}, profile:[military_service_status-i2]= {}'.format(score, profile.military_service_status))

        score = rds.get_score_of_rules_profile_recommended_to_others_counts_h8(profile.recommended_to_others_count)
        # normalized_score = calculate_normalized_score(H8_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, score)
        # normalized_profile_score += normalized_score
        profile_score += score
        self.scores_dict[HISTORIES_SCORE] = self.scores_dict.get(HISTORIES_SCORE) + score
        print('score= {}, profile:[recommended_to_others_count-h8]= {}'.format(score,
                                                                               profile.recommended_to_others_count))

        score = rds.get_score_of_rules_profile_sim_card_ownerships_i3(profile.sim_card_ownership)
        # normalized_score = calculate_normalized_score(I3_RULES_PROFILE_SIM_CARD_OWNERSHIPS, score)
        # normalized_profile_score += normalized_score
        # profile_score += score
        self.scores_dict[IDENTITIES_SCORE] = self.scores_dict.get(IDENTITIES_SCORE) + score
        print('score= {}, profile:[sim_card_ownership-i3]= {}'.format(score, profile.sim_card_ownership))

        score = rds.get_score_of_rules_profile_star_counts_avgs_h9(profile.star_count_average)
        # normalized_score = calculate_normalized_score(H9_RULES_PROFILE_STAR_COUNTS_AVGS, score)
        # normalized_profile_score += normalized_score
        profile_score += score
        self.scores_dict[HISTORIES_SCORE] = self.scores_dict.get(HISTORIES_SCORE) + score
        print('score= {}, profile:[star_count_average-h9]= {}'.format(score, profile.star_count_average))

        # print('............. profile score = {} , normalized_score = {} ................\n'.format(profile_score, normalized_profile_score))
        print('............. profile score = {} ................'.format(profile_score))
        print('... IDENTITIES_SCORE= {} , HISTORIES_SCORE= {}, VOLUMES_SCORE= {}, TIMELINESS_SCORE= {} \n'
              .format(self.scores_dict.get(IDENTITIES_SCORE), self.scores_dict.get(HISTORIES_SCORE),
                      self.scores_dict.get(VOLUMES_SCORE), self.scores_dict.get(TIMELINESS_SCORE)))
        return profile_score

    def calculate_user_done_trades_score(self, user_id: long, reset_cache=False, done_trade_object: DoneTrade = None):
        if done_trade_object is not None:
            done_trade = done_trade_object
        else:
            done_trade: DoneTrade = DoneTrade.objects(user_id=user_id).first()

        rds: RedisCachingRulesDoneTrades = self.rds.get_redis_caching_rules_done_trades_service(reset_cache)
        done_trades_score = 0
        normalized_done_trades_score = 0

        score = rds.get_score_of_rules_done_timely_trades_of_last_3_months_h6(
            done_trade.timely_trades_count_of_last_3_months)
        # normalized_score = calculate_normalized_score(H6_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, score)
        # normalized_done_trades_score += normalized_score
        done_trades_score += score
        self.scores_dict[HISTORIES_SCORE] = self.scores_dict.get(HISTORIES_SCORE) + score
        print('score= {}, doneTrades:[timely_trades_count_of_last_3_months-h6]= {}'.format(score,
                                                                                           done_trade.timely_trades_count_of_last_3_months))

        score = rds.get_score_of_rules_done_timely_trades_between_last_3_to_12_months_h7(
            done_trade.timely_trades_count_between_last_3_to_12_months)
        # normalized_score = calculate_normalized_score(H7_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, score)
        # normalized_done_trades_score += normalized_score
        done_trades_score += score
        self.scores_dict[HISTORIES_SCORE] = self.scores_dict.get(HISTORIES_SCORE) + score
        print('score= {}, doneTrades:[timely_trades_count_between_last_3_to_12_months-h7]= {}'
              .format(score, done_trade.timely_trades_count_between_last_3_to_12_months))

        score = rds.get_score_of_rules_done_past_due_trades_of_last_3_months_t22(
            done_trade.past_due_trades_count_of_last_3_months)
        # normalized_score = calculate_normalized_score(T22_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, score)
        # normalized_done_trades_score += normalized_score
        done_trades_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print(
            'score= {}, doneTrades:[past_due_trades_count_of_last_3_months-t22]= {}'.format(score,
                                                                                            done_trade.past_due_trades_count_of_last_3_months))

        score = rds.get_score_of_rules_done_past_due_trades_between_last_3_to_12_months_t23(
            done_trade.past_due_trades_count_between_last_3_to_12_months)
        # normalized_score = calculate_normalized_score(T23_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, score)
        # normalized_done_trades_score += normalized_score
        done_trades_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, doneTrades:[past_due_trades_count_between_last_3_to_12_months-t23]= {}'.
              format(score, done_trade.past_due_trades_count_between_last_3_to_12_months))

        score = rds.get_score_of_rules_done_arrear_trades_of_last_3_months_t24(
            done_trade.arrear_trades_count_of_last_3_months)
        # normalized_score = calculate_normalized_score(T24_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, score)
        # normalized_done_trades_score += normalized_score
        done_trades_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, doneTrades:[arrear_trades_count_of_last_3_months-t24]= {}'.format(score,
                                                                                            done_trade.arrear_trades_count_of_last_3_months))

        score = rds.get_score_of_rules_done_arrear_trades_between_last_3_to_12_months_t25(
            done_trade.arrear_trades_count_between_last_3_to_12_months)
        # normalized_score = calculate_normalized_score(T25_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, score)
        # normalized_done_trades_score += normalized_score
        done_trades_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, doneTrades:[arrear_trades_count_between_last_3_to_12_months-t25]= {}'
              .format(score, done_trade.arrear_trades_count_between_last_3_to_12_months))

        # calculate average of total balance
        # todo: should calculate all users' trades total balance
        avg_total_balance = 0 if GENERAL_AVG_DEAL_AMOUNT == 0 else done_trade.trades_total_balance / GENERAL_AVG_DEAL_AMOUNT
        avg_total_balance = float(avg_total_balance)
        score = rds.get_score_of_rules_done_trades_average_total_balance_ratios_v12(avg_total_balance)
        # normalized_score = calculate_normalized_score(V12_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, score)
        # normalized_done_trades_score += normalized_score
        done_trades_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, doneTrades:[avg_total_balance-v12]= {}'.format(score, avg_total_balance))

        # calculate average of all users delay days
        # todo: should calculate all users' average of done trades delay days (general_avg_delay_days)
        # general_avg_delay_days = 0
        avg_delay_days = 0 if GENERAL_AVG_DELAY_DAYS == 0 else int(done_trade.total_delay_days) / GENERAL_AVG_DELAY_DAYS
        score = rds.get_score_of_rules_done_trades_average_delay_days_t28(avg_delay_days)
        # normalized_score = calculate_normalized_score(T28_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, score)
        # normalized_done_trades_score += normalized_score
        done_trades_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, doneTrades:[avg_delay_days-t28]= {}'.format(score, done_trade.total_delay_days))

        # print('............. doneTrades_score = {} , normalized_score = {} ................\n'.
        # format(done_trades_score, normalized_done_trades_score))

        print('............. doneTrades_score = {} ................'.format(done_trades_score,
                                                                            normalized_done_trades_score))
        print('... IDENTITIES_SCORE= {} , HISTORIES_SCORE= {}, VOLUMES_SCORE= {}, TIMELINESS_SCORE= {} \n'
              .format(self.scores_dict.get(IDENTITIES_SCORE), self.scores_dict.get(HISTORIES_SCORE),
                      self.scores_dict.get(VOLUMES_SCORE), self.scores_dict.get(TIMELINESS_SCORE)))
        return done_trades_score

    def calculate_user_undone_trades_score(self, user_id: long, reset_cache=False, undone_trade_object: UndoneTrade = None, done_trade_object: DoneTrade = None):
        if undone_trade_object is not None:
            undone_trade = undone_trade_object
        else:
            undone_trade: UndoneTrade = UndoneTrade.objects(user_id=user_id).first()

        if done_trade_object is not None:
            done_trade = done_trade_object
        else:
            done_trade: DoneTrade = DoneTrade.objects(user_id=user_id).first()
        rds: RedisCachingRulesUndoneTrades = self.rds.get_redis_caching_rules_undone_trades_service(reset_cache)
        undone_trades_score = 0
        normalized_undone_trades_score = 0

        score = rds.get_score_of_rules_undone_undue_trades_counts_h10(undone_trade.undue_trades_count)
        # normalized_score = calculate_normalized_score(H10_RULES_UNDONE_UNDUE_TRADES_COUNTS, score)
        # normalized_undone_trades_score += normalized_score
        undone_trades_score += score
        self.scores_dict[HISTORIES_SCORE] = self.scores_dict.get(HISTORIES_SCORE) + score
        print('score= {}, undoneTrades:[undue_trades_count-h10]= {}'.format(score, undone_trade.undue_trades_count))

        # calculate undue_total_balance_ratio
        undue_total_balance_ratio = float(
            undone_trade.undue_trades_total_balance_of_last_year / done_trade.trades_total_balance)
        score = rds.get_score_of_rules_undone_undue_trades_total_balance_of_last_year_ratios_v15(
            undue_total_balance_ratio)
        # normalized_score = calculate_normalized_score(V15_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, score)
        # normalized_undone_trades_score += normalized_score
        undone_trades_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, undoneTrades:[undue_total_balance_ratio-v15]= {}'.format(score, undue_total_balance_ratio))

        score = rds.get_score_of_rules_undone_past_due_trades_counts_t26(undone_trade.past_due_trades_count)
        # normalized_score = calculate_normalized_score(T26_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, score)
        # normalized_undone_trades_score += normalized_score
        undone_trades_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, undoneTrades:[past_due_trades_count-t26]= {}'.format(score, undone_trade.past_due_trades_count))

        timely_done_trades_of_last_year = (done_trade.timely_trades_count_of_last_3_months + done_trade.timely_trades_count_between_last_3_to_12_months)
        # calculate past_due_total_balance_ratio
        past_due_total_balance_ratio = float(
            undone_trade.past_due_trades_total_balance_of_last_year / done_trade.trades_total_balance)
        score = rds.get_score_of_rules_undone_past_due_trades_total_balance_of_last_year_ratios_v13(
            past_due_total_balance_ratio)
        score_code = rds.get_score_code_of_rules_undone_past_due_trades_total_balance_of_last_year_ratios_v13(
            past_due_total_balance_ratio)
        if timely_done_trades_of_last_year == 1 and score_code == SCORE_CODE_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS:
            score *= 2

        # normalized_score = calculate_normalized_score(V13_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, score)
        # normalized_undone_trades_score += normalized_score
        undone_trades_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, undoneTrades:[past_due_total_balance_ratio-v13]= {}'.format(score,past_due_total_balance_ratio))

        score = rds.get_score_of_rules_undone_arrear_trades_counts_t27(undone_trade.arrear_trades_count)
        # normalized_score = calculate_normalized_score(T27_RULES_UNDONE_ARREAR_TRADES_COUNTS, score)
        # normalized_undone_trades_score += normalized_score
        undone_trades_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, undoneTrades:[arrear_trades_count-t27]= {}'.format(score, undone_trade.arrear_trades_count))

        # calculate arrear_total_balance_ratio
        arrear_total_balance_ratio = float(
            undone_trade.arrear_trades_total_balance_of_last_year / done_trade.trades_total_balance)
        score = rds.get_score_of_rules_undone_arrear_trades_total_balance_of_last_year_ratios_v14(
            arrear_total_balance_ratio)
        score_code = rds.get_score_code_of_rules_undone_arrear_trades_total_balance_of_last_year_ratios_v14(
            arrear_total_balance_ratio)
        if timely_done_trades_of_last_year == 1 and score_code == SCORE_CODE_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS:
            score *= 2
        # normalized_score = calculate_normalized_score(V14_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, score)
        # normalized_undone_trades_score += normalized_score
        undone_trades_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, undoneTrades:[arrear_total_balance_ratio-v14]= {}'.format(score, arrear_total_balance_ratio))

        # print('............. undoneTrades_score = {} , normalized_score = {} ................\n'.format(undone_trades_score,
        # normalized_undone_trades_score))

        print('............. undoneTrades_score = {} ................'.format(undone_trades_score))
        print('... IDENTITIES_SCORE= {} , HISTORIES_SCORE= {}, VOLUMES_SCORE= {}, TIMELINESS_SCORE= {} \n'
              .format(self.scores_dict.get(IDENTITIES_SCORE), self.scores_dict.get(HISTORIES_SCORE),
                      self.scores_dict.get(VOLUMES_SCORE), self.scores_dict.get(TIMELINESS_SCORE)))
        return undone_trades_score

    def calculate_user_loans_score(self, user_id: long, reset_cache=False, loan_object: Loan = None):
        if loan_object is not None:
            loan = loan_object
        else:
            loan: Loan = Loan.objects(user_id=user_id).first()

        rds: RedisCachingRulesLoans = self.rds.get_redis_caching_rules_loans_service(reset_cache)
        loans_score = 0
        normalized_loans_score = 0

        score = rds.get_score_of_rules_loans_total_counts_h11(loan.loans_total_count)
        # normalized_score = calculate_normalized_score(H11_RULES_LOAN_TOTAL_COUNTS, score)
        # normalized_loans_score += normalized_score
        loans_score += score
        self.scores_dict[HISTORIES_SCORE] = self.scores_dict.get(HISTORIES_SCORE) + score
        print('score= {}, loans:[loans_total_count-h11]= {}'.format(score, loan.loans_total_count))

        # should be calculate avg_of_all_users_monthly_installment_total_balance
        installments_total_balance_ratio = 0 if ALL_USERS_AVERAGE_MONTHLY_INSTALLMENT_AMOUNT == 0 else float(
            loan.monthly_installments_total_balance / ALL_USERS_AVERAGE_MONTHLY_INSTALLMENT_AMOUNT)

        score = rds.get_score_of_rules_loan_monthly_installments_total_balance_ratios_v16(
            installments_total_balance_ratio)
        # normalized_score = calculate_normalized_score(V16_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, score)
        # normalized_loans_score += normalized_score
        loans_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, loans:[installments_total_balance_ratio-v16]= {}'.format(score,
                                                                                   installments_total_balance_ratio))

        # should be calculate user_total_loans_balance
        overdue_total_balance_ratio = 0 if loan.loans_total_balance == 0 else float(
            loan.overdue_loans_total_balance / loan.loans_total_balance)
        score = rds.get_score_of_rules_overdue_loans_total_balance_ratios_v18(overdue_total_balance_ratio)
        # normalized_score = calculate_normalized_score(V18_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, score)
        # normalized_loans_score += normalized_score
        loans_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, loans:[overdue_total_balance_ratio-v18]= {}'.format(score, overdue_total_balance_ratio))

        score = rds.get_score_of_rules_past_due_loans_total_counts_t33(loan.past_due_loans_total_count)
        # normalized_score = calculate_normalized_score(T33_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, score)
        # normalized_loans_score += normalized_score
        loans_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, loans:[past_due_loans_total_count-t33]= {}'.format(score, loan.past_due_loans_total_count))

        # should be calculate user_total_loans_balance
        past_due_total_balance_ratio = 0 if loan.loans_total_balance == 0 else float(
            loan.past_due_loans_total_balance / loan.loans_total_balance)
        score = rds.get_score_of_rules_past_due_loans_total_balance_ratios_v19(past_due_total_balance_ratio)
        # normalized_score = calculate_normalized_score(V19_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS, score)
        # normalized_loans_score += normalized_score
        loans_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, loans:[past_due_total_balance_ratio-v19]= {}'.format(score, past_due_total_balance_ratio))

        score = rds.get_score_of_rules_arrear_loans_total_counts_t34(loan.arrear_loans_total_count)
        # normalized_score = calculate_normalized_score(T34_RULES_LOAN_ARREAR_TOTAL_COUNTS, score)
        # normalized_loans_score += normalized_score
        loans_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, loans:[arrear_loans_total_count-t34]= {}'.format(score, loan.arrear_loans_total_count))

        # should be calculate user_total_loans_balance
        arrear_total_balance_ratio = 0 if loan.loans_total_balance == 0 else float(
            loan.arrear_loans_total_balance / loan.loans_total_balance)
        score = rds.get_score_of_rules_arrear_loans_total_balance_ratios_v20(arrear_total_balance_ratio)
        # normalized_score = calculate_normalized_score(V20_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, score)
        # normalized_loans_score += normalized_score
        loans_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, loans:[arrear_total_balance_ratio-v20]= {}'.format(score, arrear_total_balance_ratio))

        score = rds.get_score_of_rules_suspicious_loans_total_counts_t35(loan.suspicious_loans_total_count)
        # normalized_score = calculate_normalized_score(T35_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS, score)
        # normalized_loans_score += normalized_score
        # loans_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print(
            'score= {}, loans:[suspicious_loans_total_count-t35]= {}'.format(score, loan.suspicious_loans_total_count))

        # should be calculate user_total_loans_balance
        suspicious_total_balance_ratio = 0 if loan.loans_total_balance == 0 else float(
            loan.suspicious_loans_total_balance / loan.loans_total_balance)
        score = rds.get_score_of_rules_suspicious_loans_total_balance_ratios_v21(suspicious_total_balance_ratio)
        # normalized_score = calculate_normalized_score(V21_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, score)
        # normalized_loans_score += normalized_score
        loans_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, loans:[suspicious_total_balance_ratio-v21]= {}'.format(score, suspicious_total_balance_ratio))

        # print('............. loans_score = {} , normalized_score = {} ................\n'.format(loans_score, normalized_loans_score))
        print('............. loans_score = {} ................'.format(loans_score))
        print('... IDENTITIES_SCORE= {} , HISTORIES_SCORE= {}, VOLUMES_SCORE= {}, TIMELINESS_SCORE= {} \n'
              .format(self.scores_dict.get(IDENTITIES_SCORE), self.scores_dict.get(HISTORIES_SCORE),
                      self.scores_dict.get(VOLUMES_SCORE), self.scores_dict.get(TIMELINESS_SCORE)))
        return loans_score

    def calculate_user_cheques_score(self, user_id: long, reset_cache=False, cheque_object: Cheque = None):
        if cheque_object is not None:
            cheque = cheque_object
        else:
            cheque: Cheque = Cheque.objects(user_id=user_id).first()
        rds: RedisCachingRulesCheques = self.rds.get_redis_caching_rules_cheques_service(reset_cache)
        cheques_score = 0
        normalized_cheques_score = 0

        score = rds.get_score_of_rules_unfixed_returned_cheques_count_between_last_3_to_12_months_t30(
            cheque.unfixed_returned_cheques_count_between_last_3_to_12_months)
        # normalized_score = calculate_normalized_score(T30_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_BETWEEN_LAST_3_TO_12_MONTHS, score)
        # normalized_cheques_score += normalized_score
        cheques_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, cheques:[unfixed_returned_cheques_count_between_last_3_to_12_months-t30]= {}'
              .format(score, cheque.unfixed_returned_cheques_count_between_last_3_to_12_months))

        score = rds.get_score_of_rules_unfixed_returned_cheques_count_of_last_3_months_t29(
            cheque.unfixed_returned_cheques_count_of_last_3_months)
        # normalized_score = calculate_normalized_score(T29_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_LAST_3_MONTHS, score)
        # normalized_cheques_score += normalized_score
        cheques_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, cheques:[unfixed_returned_cheques_count_of_last_3_months-t29]= {}'
              .format(score, cheque.unfixed_returned_cheques_count_of_last_3_months))

        score = rds.get_score_of_rules_unfixed_returned_cheques_count_of_last_5_years_t32(
            cheque.unfixed_returned_cheques_count_of_last_5_years)
        # normalized_score = calculate_normalized_score(T32_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_LAST_5_YEARS, score)
        # normalized_cheques_score += normalized_score
        cheques_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, cheques:[unfixed_returned_cheques_count_of_last_5_years-t32]= {}'
              .format(score, cheque.unfixed_returned_cheques_count_of_last_5_years))

        score = rds.get_score_of_rules_unfixed_returned_cheques_count_of_more_12_months_t31(
            cheque.unfixed_returned_cheques_count_of_more_12_months)
        # normalized_score = calculate_normalized_score(T31_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_MORE_12_MONTHS, score)
        # normalized_cheques_score += normalized_score
        cheques_score += score
        self.scores_dict[TIMELINESS_SCORE] = self.scores_dict.get(TIMELINESS_SCORE) + score
        print('score= {}, cheques:[unfixed_returned_cheques_count_of_more_12_months]-t31= {}'
              .format(score, cheque.unfixed_returned_cheques_count_of_more_12_months))

        # should be calculate avg_of_all_users_unfixed_returned_cheques_total_balance
        total_balance_ratio = float(
            cheque.unfixed_returned_cheques_total_balance / ALL_USERS_AVERAGE_UNFIXED_RETURNED_CHEQUES_AMOUNT)
        score = rds.get_score_of_rules_unfixed_returned_cheques_total_balance_ratios_v17(total_balance_ratio)
        # normalized_score = calculate_normalized_score(V17_RULES_CHEQUE_UNFIXED_RETURNED_TOTAL_BALANCE_RATIOS, score)
        # normalized_cheques_score += normalized_score
        cheques_score += score
        self.scores_dict[VOLUMES_SCORE] = self.scores_dict.get(VOLUMES_SCORE) + score
        print('score= {}, cheques:[total_balance_ratio-v17]= {}'.format(score, total_balance_ratio))

        # print('............. cheques score = {} , normalized_score = {}  ................\n'.format(cheques_score, normalized_cheques_score))
        print('............. cheques score = {} ................'.format(cheques_score))
        print('... IDENTITIES_SCORE= {} , HISTORIES_SCORE= {}, VOLUMES_SCORE= {}, TIMELINESS_SCORE= {} \n'
              .format(self.scores_dict.get(IDENTITIES_SCORE), self.scores_dict.get(HISTORIES_SCORE),
                      self.scores_dict.get(VOLUMES_SCORE), self.scores_dict.get(TIMELINESS_SCORE)))
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
        print(
            '... timeliness_max_percent= {}, timeliness_max_score= {}, timeliness_pure_score= {}, timeliness_normalized_score= {}'
                .format(timeliness_max_percent, timeliness_max_score, timeliness_pure_score,
                        timeliness_normalized_score))
        return timeliness_normalized_score
