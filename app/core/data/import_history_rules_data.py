from typing import List

from app.core.constants import rules_max_val, PARENT, HISTORIES, CODE, H5_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, RULE_MASTER_CODE, H9_RULES_PROFILE_STAR_COUNTS_AVGS, \
    H8_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, H7_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, H6_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, H10_RULES_UNDONE_UNDUE_TRADES_COUNTS, H11_RULES_LOAN_TOTAL_COUNTS
from app.core.database import get_db
from app.core.models.rules import Rule
from app.core.services.data_service import DataService
from app.core.services.util import create_new_rule, create_new_score_change_reason


# noinspection DuplicatedCode
def import_rule_history_master(ds: DataService):
    # Delete all histories(H) rules
    l2_rules: {Rule} = ds.get_rules({PARENT: HISTORIES})
    for r in l2_rules:
        # delete all l3_rules
        ds.delete_rules({PARENT: r[CODE]})

    # delete all l2_rules
    ds.delete_rules({PARENT: HISTORIES})
    # delete the l1_rule
    ds.delete_rules({CODE: HISTORIES})
    print('Histories(H) rules are deleted.')

    # define Identities(I)' rules master: level 1
    rule = create_new_rule(1, None, 'H', 'سوابق تعاملات', 30, 270)
    ds.insert_rule(rule)
    print('Histories(H) master rule is created.')


def import_rules_history_membership_days_counts_h5(ds: DataService):
    # define History(H)' rules of membership_days master: level 2
    rule = create_new_rule(2, 'H', 'H5', 'مدت زمان عضویت فعال', 6.67, 60)
    ds.insert_rule(rule)

    # define History(H)' rules of membership_days details: level 3
    # Just Registered MembershipDaysWithAtleast1SD == 0 	00	H0501P0	عضو جدید
    rule = create_new_rule(3, 'H5', 'H0501P0', 'عضو جدید', 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    #  1 <=  MembershipDaysWithAtleast1SD ≤ 90	    10	H0502P10	 عضویت بین 1 تا 90 روز
    rule = create_new_rule(3, 'H5', 'H0502P10', ' عضویت بین 1 تا 90 روز', 1.11, 10, 1, 90)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 91 <=  MembershipDaysWithAtleast3SD ≤ 180	    20	H0503P20	 عضویت بین 91 تا 180 روز
    rule = create_new_rule(3, 'H5', 'H0503P20', 'عضویت بین 91 تا 180 روز', 2.22, 20, 91, 180)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 181 <=  MembershipDaysWithAtleast5SD ≤ 365	30	H0504P30	 عضویت بین 181 تا 365 روز
    rule = create_new_rule(3, 'H5', 'H0504P30', ' عضویت بین 181 تا 365 روز', 3.33, 30, 181, 365)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 366 <= MembershipDaysWithAtleast10SD ≤ 720	40	H0505P40	 عضویت بین 366 تا 720 روز
    rule = create_new_rule(3, 'H5', 'H0505P40', ' عضویت بین 366 تا 720 روز', 4.44, 40, 366, 720)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 721 <= MembershipDaysWithAtleast15SD ≤ 1080	50	H0506P50	 عضویت بین 721 تا 1080 روز
    rule = create_new_rule(3, 'H5', 'H0506P50', ' عضویت بین 721 تا 1080 روز', 5.50, 50, 721, 1080)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    #     MembershipDaysWithAtleast20SD >= 1081	    60	H0507P60	 عضویت بیش از 1081 روز
    rule = create_new_rule(3, 'H5', 'H0507P60', ' عضویت بیش از 1081 روز', 6.67, 60, 1081, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Histories(H) membership_days_counts_h5 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H5_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS})
    change_reason = create_new_score_change_reason(H5_RULES_PROFILE_MEMBERSHIP_DAYS_COUNTS, rule_codes, 'افزایش مدت عضویت فعال')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) membership_days_counts_h5 change reasons are created.')


def import_rules_history_done_timely_trades_of_last_3_months_h6(ds: DataService):
    # define History(H)' rules of done_timely_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'H', 'H6', 'تعداد تعاملات موفق در 3 ماه گذشته', 4.44, 40)
    ds.insert_rule(rule)

    # define History(H)' rules of done_timely_trades_of_last_3_months details: level 3
    # Last3MSD = 0	00	H0601P0	کاربر در سه ماه گذشته هیچ تعامل موفقی با سایر کاربران نداشته است
    rule = create_new_rule(3, 'H6', 'H0601P0', 'کاربر در سه ماه گذشته هیچ تعامل موفقی با سایر کاربران نداشته است', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # Last3MSD = 1	10	H0602P10	کاربر در سه ماه گذشته 1 تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H6', 'H0602P10', 'کاربر در سه ماه گذشته 1 تعامل موفق با سایر کاربران داشته است', 1.11, 10, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Last3MSD = 2	20	H0603P20	کاربر در سه ماه گذشته ۲ تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H6', 'H0603P20', 'کاربر در سه ماه گذشته ۲ تعامل موفق با سایر کاربران داشته است', 2.22, 20, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Last3MSD = 3	30	H0604P30	کاربر در سه ماه گذشته 3 تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H6', 'H0601P0', 'کاربر در سه ماه گذشته 3 تعامل موفق با سایر کاربران داشته است', 3.33, 30, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Last3MSD ≥ 4	40	H0605P40	کاربر در سه ماه گذشته بیش از 3 تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H6', 'H0605P40', 'کاربر در سه ماه گذشته بیش از 3 تعامل موفق با سایر کاربران داشته است', 4.44, 40, 4, 4)
    ds.insert_rule(rule)
    print('Histories(H) done_timely_trades_of_last_3_months_h6 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H6_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS})
    change_reason = create_new_score_change_reason(H6_RULES_DONE_TIMELY_TRADES_OF_LAST_3_MONTHS, rule_codes, 'افزایش معاملات موفق در سه ماه گذشته', 'کاهش معاملات موفق در سه ماه گذشته')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) done_timely_trades_of_last_3_months_h6 change reasons are created.')


def import_rules_history_done_timely_trades_between_last_3_to_12_months_h7(ds: DataService):
    # define History(H)' rules of done_timely_trades_between_last_3_to_12_months master: level 2
    rule = create_new_rule(2, 'H', 'H7', 'تعداد تعاملات موفق در ۳ تا ۱۲ ماه گذشته', 4.44, 40)
    ds.insert_rule(rule)

    # define History(H)' rules of done_timely_trades_of_last_3_months details: level 3
    # Last1YSD = 0	00	H0701P0	کاربر در یکسال گذشته هیچ تعامل موفقی با سایر کاربران نداشته است
    rule = create_new_rule(3, 'H7', 'H0701P0', 'کاربر در یکسال گذشته هیچ تعامل موفقی با سایر کاربران نداشته است', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # Last1YSD = 1	05	H0702P05	کاربر در یکسال گذشته 1 تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H7', 'H0702P05', 'کاربر در یکسال گذشته 1 تعامل موفق با سایر کاربران داشته است', 0.56, 5, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2 <= Last1YSD ≤ 3	10	H0703P10	کاربر در یکسال گذشته بین 2 تا 3 تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H7', 'H0703P10', 'کاربر در یکسال گذشته بین 2 تا 3 تعامل موفق با سایر کاربران داشته است', 1.11, 10, 2, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 <= Last1YSD ≤ 6	20	H0704P20	کاربر در یکسال گذشته بین 4 تا 6 تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H7', 'H0704P20', 'کاربر در یکسال گذشته بین 4 تا 6 تعامل موفق با سایر کاربران داشته است', 2.22, 20, 4, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= Last1YSD ≤ 10	30	H0705P30	کاربر در یکسال گذشته بین 7 تا 10 تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H7', 'H0705P30', 'کاربر در یکسال گذشته بین 7 تا 10 تعامل موفق با سایر کاربران داشته است', 3.33, 30, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Last1YSD >= 11	40	H0706P40	کاربر در یکسال گذشته بیش از 10 تعامل موفق با سایر کاربران داشته است
    rule = create_new_rule(3, 'H7', 'H0706P40', 'کاربر در یکسال گذشته بیش از 10 تعامل موفق با سایر کاربران داشته است', 4.44, 40, 11,
                           rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Histories(H) done_timely_trades_between_last_3_to_12_months_h7 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H7_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS})
    change_reason = create_new_score_change_reason(H7_RULES_DONE_TIMELY_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rule_codes, 'افزایش معاملات موفق در یک سال گذشته', 'کاهش معاملات موفق در یک سال گذشته')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) done_timely_trades_between_last_3_to_12_months_h7 change reasons are created.')


def import_rules_history_recommended_to_others_counts_h8(ds: DataService):
    # define History(H)' rules of recommended_to_others_counts master: level 2
    rule = create_new_rule(2, 'H', 'H8', 'پیشنهاد شدن کاربر به سایرین جهت انجام تعامل پس از انجام موفقیت آمیز تعامل', 4.44, 40)
    ds.insert_rule(rule)

    # define History(H)' rules of recommended_to_others_counts details: level 3
    # Recommendation = 0	00	H0801P0	کاربر توسط کسی پیشنهاد نشده است
    rule = create_new_rule(3, 'H8', 'H0801P0', 'کاربر توسط کسی پیشنهاد نشده است', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # Recommendation = 1	10	H0802P10	پیشنهاد شده توسط 1 نفر
    rule = create_new_rule(3, 'H8', 'H0802P10', 'پیشنهاد شده توسط 1 نفر', 1.11, 10, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2 < Recommendation ≤ 3	20	H0803P20	پیشنهاد شده توسط 2 تا 3 نفر
    rule = create_new_rule(3, 'H8', 'H0803P20', 'پیشنهاد شده توسط 2 تا 3 نفر', 2.22, 20, 2, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 < Recommendation ≤ 10	30	H0804P30	پیشنهاد شده توسط 4 تا 10 نفر
    rule = create_new_rule(3, 'H8', 'H0804P30', 'پیشنهاد شده توسط 4 تا 10 نفر', 3.33, 30, 4, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 11 < Recommendation ≤ 30	40	H0805P40	پیشنهاد شده توسط 11 تا 30 نفر
    rule = create_new_rule(3, 'H8', 'H0805P40', 'پیشنهاد شده توسط 11 تا 30 نفر', 4.44, 40, 11, 30)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Recommendation > 30	50	H0806P50	پیشنهاد شده توسط بیش از 30 نفر
    rule = create_new_rule(3, 'H8', 'H0806P50', 'پیشنهاد شده توسط بیش از 30 نفر', 5.56, 50, 30, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Histories(H) recommended_to_others_counts_h8 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H8_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS})
    change_reason = create_new_score_change_reason(H8_RULES_PROFILE_RECOMMENDED_TO_OTHERS_COUNTS, rule_codes, 'افزایش پیشنهادات طرفین معاملات به سایرین جهت انجام معامله با شما', 'کاهش پیشنهادات طرفین معاملات به سایرین جهت انجام معامله با شما')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) recommended_to_others_counts_h8 change reasons are created.')


def import_rules_history_star_counts_avgs_h9(ds: DataService):
    # define History(H)' rules of star_counts_avgs master: level 2
    rule = create_new_rule(2, 'H', 'H9', ' امتیاز رضایتمندی دریافت شده از طرف مقابل پس از انجام موفقیت آمیز تعامل', 5.56, 50)
    ds.insert_rule(rule)

    # define History(H)' rules of star_counts_avgs details: level 3
    # WeightedAveStars <= 1	00	H0901P0	کاربر به طور متوسط کمتر مساوی ۱ ستاره کسب کرده است
    rule = create_new_rule(3, 'H9', 'H0901P0', 'کاربر به طور متوسط کمتر مساوی ۱ ستاره کسب کرده است', 0, 0, 0, 1)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 1.001 <= WeightedAveStars ≤ 2	05	H0902P5	کاربر به طور متوسط بیش از ۱ و کمتر مساوی ۲ ستاره کسب کرده است
    rule = create_new_rule(3, 'H9', 'H0902P5', 'کاربر به طور متوسط بیش از ۱ و کمتر مساوی ۲ ستاره کسب کرده است', 0.56, 5, 1.001, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2.001 <= WeightedAveStars ≤ 3	10	H0903P10	کاربر به طور متوسط بیش از ۲ و کمتر مساوی ۳ ستاره کسب کرده است
    rule = create_new_rule(3, 'H9', 'H0903P10', 'کاربر به طور متوسط بیش از ۲ و کمتر مساوی ۳ ستاره کسب کرده است', 1.11, 10, 2.001, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 3.001 <= WeightedAveStars ≤ 4	30	H0904P30	کاربر به طور متوسط بیش از ۳ و کمتر مساوی ۴ ستاره کسب کرده است
    rule = create_new_rule(3, 'H9', 'H0904P30', 'کاربر به طور متوسط بیش از ۳ و کمتر مساوی ۴ ستاره کسب کرده است', 3.33, 30, 3.001, 4)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4.001 <= WeightedAveStars ≤ 5	50	H0905P50	کاربر به طور متوسط بیش از ۴ و کمتر مساوی ۵ ستاره کسب کرده است
    rule = create_new_rule(3, 'H9', 'H0905P50', 'کاربر به طور متوسط بیش از ۴ و کمتر مساوی ۵ ستاره کسب کرده است', 5.56, 50, 4.001, 5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Histories(H) star_counts_avgs_h9 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H9_RULES_PROFILE_STAR_COUNTS_AVGS})
    change_reason = create_new_score_change_reason(H9_RULES_PROFILE_STAR_COUNTS_AVGS, rule_codes, 'افزایش امتیاز رضایتمندی دریافت شده از طرفین معاملات', 'کاهش امتیاز رضایتمندی دریافت شده از طرفین معاملات')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) star_counts_avgs_h9 change reasons are created.')


def import_rules_history_undone_undue_trades_counts_h10(ds: DataService):
    # define History(H)' rules of undone_undue_trades_counts master: level 2
    rule = create_new_rule(2, 'H', 'H10', 'تعداد تعاملات جاری سررسید نشده', 1.11, 10)
    ds.insert_rule(rule)

    # define History(H)' rules of undone_undue_trades_counts details: level 3
    # NumNotDueDeal = 0 00 	H1001P0	کاربر تعامل سررسید نشده ندارد
    rule = create_new_rule(3, 'H10', 'H1001P0', 'کاربر تعامل سررسید نشده ندارد', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # NumNotDueDeal = 1 02	H1002P2	کاربر 1 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1002P2', 'کاربر 1 تعامل سررسید نشده دارد', 0.22, 2, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # NumNotDueDeal = 2	05	H1003P5	کاربر 2 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1003P5', 'کاربر 2 تعامل سررسید نشده دارد', 0.56, 5, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # NumNotDueDeal = 3	7	H1004P7	کاربر 3 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1004P7', 'کاربر 3 تعامل سررسید نشده دارد', 0.78, 7, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # NumNotDueDeal = 4	10	H1005P10	کاربر 4 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1005P10', 'کاربر 4 تعامل سررسید نشده دارد', 1.11, 10, 4, 4)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H10_RULES_UNDONE_UNDUE_TRADES_COUNTS})
    change_reason = create_new_score_change_reason(H10_RULES_UNDONE_UNDUE_TRADES_COUNTS, rule_codes, 'افزایش امکان سنجش رفتار اعتباری کاربر از طریق افزایش معاملات جاری', 'کاهش امکان سنجش رفتار اعتباری کاربر به دلیل کاهش معاملات جاری')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) undone_undue_trades_counts_h10 part1 change reasons are created.')

    # NumNotDueDeal = 5	03	H1006P3	کاربر 5 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1006P3', 'کاربر 5 تعامل سررسید نشده دارد', 0.33, 3, 5, 5)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # NumNotDueDeal = 6	-1	H1007N1	کاربر 6 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1007N1', 'کاربر 6 تعامل سررسید نشده دارد', 0.11, -1, 6, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= NumNotDueDeal ≤ 10	-10	H1008N10	کاربر بین 7 تا 10 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1008N10', 'کاربر بین 7 تا 10 تعامل سررسید نشده دارد', 1.11, -10, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 11 <= NumNotDueDeal ≤ 20	-20	H1009N20	کاربر بین 11 تا 20 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1009N20', 'کاربر بین 11 تا 20 تعامل سررسید نشده دارد', 2.22, -20, 11, 20)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 21 <= NumNotDueDeal ≤ 30	-30	H1010N30	کاربر بین 21 تا 30 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1010N30', 'کاربر بین 21 تا 30 تعامل سررسید نشده دارد', 3.33, -30, 21, 30)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # NotDueDeal >= 31	-50	H1011N50	کاربر بیش از 30 تعامل سررسید نشده دارد
    rule = create_new_rule(3, 'H10', 'H1011N50', 'کاربر بیش از 30 تعامل سررسید نشده دارد', 5.56, -50, 31, 999)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Histories(H) undone_undue_trades_counts_h10 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H10_RULES_UNDONE_UNDUE_TRADES_COUNTS})
    change_reason = create_new_score_change_reason(H10_RULES_UNDONE_UNDUE_TRADES_COUNTS, rule_codes, 'کاهش تعداد معاملات جاری', 'افزایش بیش از حد تعداد معاملات جاری')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) undone_undue_trades_counts_h10 part2 change reasons are created.')


def import_rules_history_loans_total_count_h11(ds: DataService):
    # define History(H)' rules of undone_undue_trades_counts master: level 2
    rule = create_new_rule(2, 'H', 'H11', 'تعداد کل تسهیلات بانکی در جریان', 2.22, 20)
    ds.insert_rule(rule)

    # define History(H)' rules of undone_undue_trades_counts details: level 3
    # Loans = 0	00	H1101P0	کاربر هیچگونه تسهیلات در جریان ندارد
    rule = create_new_rule(3, 'H11', 'H1101P0', 'کاربر هیچگونه تسهیلات در جریان ندارد', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # Loans = 1	20	H1102P20	کاربر ۱ تسهیلات در جریان دارد
    rule = create_new_rule(3, 'H11', 'H1102P20', 'کاربر ۱ تسهیلات در جریان دارد', 2.22, 20, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H11_RULES_LOAN_TOTAL_COUNTS})
    change_reason = create_new_score_change_reason(H11_RULES_LOAN_TOTAL_COUNTS, rule_codes, 'افزایش امکان سنجش رفتار اعتباری کاربر از طریق اخذ تسهیلات بانکی', 'کاهش امکان سنجش رفتار اعتباری کاربر به دلیل اتمام تسهیلات بانکی')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) loans_total_count_h11 part-1 change reasons are created.')

    # Loans = 2	10	H1103P10	کاربر ۲ تسهیلات در جریان دارد
    rule = create_new_rule(3, 'H11', 'H1103P10', 'کاربر ۲ تسهیلات در جریان دارد', 1.11, 10, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Loans = 3	01	H1104P1	کاربر ۳ تسهیلات در جریان دارد
    rule = create_new_rule(3, 'H11', 'H1104P1', 'کاربر ۳ تسهیلات در جریان دارد', 0.11, 1, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Loans = 4	-20	H1105N20	کاربر ۴ تسهیلات در جریان دارد
    rule = create_new_rule(3, 'H11', 'H1105N20', 'کاربر ۴ تسهیلات در جریان دارد', 2.22, -20, 4, 4)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Loans = 5	-30	H1106N30	کاربر ۵ تسهیلات در جریان دارد
    rule = create_new_rule(3, 'H11', 'H1106N30', 'کاربر ۵ تسهیلات در جریان دارد', 3.33, -30, 5, 5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # Loans >= 6	-50	H1107N50	کاربر بیش از ۵ تسهیلات در جریان دارد
    rule = create_new_rule(3, 'H11', 'H1107N50', 'کاربر بیش از ۵ تسهیلات در جریان دارد', 5.56, -50, 6, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Histories(H) loans_total_count_h11 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: H11_RULES_LOAN_TOTAL_COUNTS})
    change_reason = create_new_score_change_reason(H11_RULES_LOAN_TOTAL_COUNTS, rule_codes, 'کاهش تعداد تسهیلات بانکی در جریان', 'افزایش تعداد تسهیلات بانکی در جریان')
    ds.insert_score_change_reason(change_reason)
    print('Histories(H) loans_total_count_h11 part-2 change reasons are created.')


def import_rules_histories(ds: DataService):
    import_rule_history_master(ds)
    import_rules_history_membership_days_counts_h5(ds)
    import_rules_history_done_timely_trades_of_last_3_months_h6(ds)
    import_rules_history_done_timely_trades_between_last_3_to_12_months_h7(ds)
    import_rules_history_recommended_to_others_counts_h8(ds)
    import_rules_history_star_counts_avgs_h9(ds)
    import_rules_history_undone_undue_trades_counts_h10(ds)
    import_rules_history_loans_total_count_h11(ds)


if __name__ == '__main__':
    import_rules_histories(DataService(get_db()))
