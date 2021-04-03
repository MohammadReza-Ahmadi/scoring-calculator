from typing import List

from app.core.constants import rules_max_val, TIMELINESS, PARENT, CODE, T22_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, RULE_MASTER_CODE, T23_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, T24_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, \
    T25_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, T26_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, T27_RULES_UNDONE_ARREAR_TRADES_COUNTS, T28_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, T29_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_LAST_3_MONTHS, \
    T30_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_BETWEEN_LAST_3_TO_12_MONTHS, T31_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_MORE_12_MONTHS, T32_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_LAST_5_YEARS, T33_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, T34_RULES_LOAN_ARREAR_TOTAL_COUNTS, \
    T35_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS
from app.core.database import get_db
from app.core.models.rules import Rule
from app.core.services.data_service import DataService
from app.core.services.util import create_new_rule, create_new_score_reason


# noinspection DuplicatedCode
def import_rule_timeliness_master(ds: DataService):
    # Delete all Timeliness(T) rules
    l2_rules: {Rule} = ds.get_rules({PARENT: TIMELINESS})
    for r in l2_rules:
        # delete all l3_rules
        ds.delete_rules({PARENT: r[CODE]})

    # delete all l2_rules
    ds.delete_rules({PARENT: TIMELINESS})
    # delete the l1_rule
    ds.delete_rules({CODE: TIMELINESS})
    print('Timeliness(T) rules are deleted.')

    # define Timeliness(T)' rules master: level 1
    # rule.drop_collection()
    rule = create_new_rule(1, None, 'T', 'انجام به موقع تعهدات', 35, 270)
    ds.insert_rule(rule)
    print('Timeliness(T) master rule is created.')


# تعداد تعاملات موفق در 3 ماه گذشته
def import_rules_timeliness_done_past_due_trades_of_last_3_months_t22(ds: DataService):
    # define Timeliness(T)' rules of done_past_due_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T22', 'تعداد تعاملات سررسید گذشته (کمتر از 30 روز تاخیر) خاتمه یافته در ۳ ماه گذشته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_past_due_trades_of_last_3_months details: level 3
    # B30DayDelayLast3M = 0	20	T2201P20	کاربر در سه ماه گذشته هیچ تعامل سررسید گذشته‌ای نداشته است
    rule = create_new_rule(3, 'T22', 'T2201P20', 'کاربر در سه ماه گذشته هیچ تعامل سررسید گذشته‌ای نداشته است', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # B30DayDelayLast3M = 1	10	T2202P10	کاربر در سه ماه گذشته 1 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T22', 'T2202P10', 'کاربر در سه ماه گذشته 1 تعامل سررسید گذشته‌ داشته است', 1.30, 10, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2 < B30DayDelayLast3M ≤ 3	00	T2203P0	کاربر در سه ماه گذشته بین 2 تا 3 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T22', 'T2203P0', 'کاربر در سه ماه گذشته بین 2 تا 3 تعامل سررسید گذشته‌ داشته است', 0, 0, 2, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 <= B30DayDelayLast3M ≤ 6	-10	T2204N10	کاربر در سه ماه گذشته بین 4 تا 6 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T22', 'T2204N10', 'کاربر در سه ماه گذشته بین 4 تا 6 تعامل سررسید گذشته‌ داشته است', 1.30, -10, 4, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= B30DayDelayLast3M ≤ 10	-20	T2205N20	کاربر در سه ماه گذشته بین 7 تا 10 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T22', 'T2205N20', 'کاربر در سه ماه گذشته بین 7 تا 10 تعامل سررسید گذشته‌ داشته است', 2.59, -20, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # B30DayDelayLast3M >= 11	-30	T2206N30	کاربر در سه ماه گذشته بیش از 10 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T22', 'T2206N30', 'کاربر در سه ماه گذشته بیش از 10 تعامل سررسید گذشته‌ داشته است', 3.89, -30, 11,
                           rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) done_past_due_trades_of_last_3_months_t22 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T22_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS})
    change_reason = create_new_score_reason(T22_RULES_DONE_PAST_DUE_TRADES_OF_LAST_3_MONTHS, rule_codes, 'کاهش تعداد معاملات سررسید گذشته خاتمه یافته در سه ماه گذشته', 'افزایش تعداد معاملات سررسید گذشته خاتمه یافته در سه ماه گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) done_past_due_trades_of_last_3_months_t22 change reasons are created.')


def import_rules_timeliness_done_past_due_trades_between_last_3_to_12_months_t23(ds: DataService):
    # define Timeliness(T)' rules of done_past_due_trades_between_last_3_to_12_months master: level 2
    rule = create_new_rule(2, 'T', 'T23', 'تعداد تعاملات سررسید گذشته (کمتر از 30 روز تاخیر) خاتمه یافته در ۳ تا ۱۲ ماه گذشته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_past_due_trades_between_last_3_to_12_months details: level 3
    # B30DayDelayLast3-12M = 0	20	T2301P20	کاربر در یکسال گذشته هیچ تعامل سررسید گذشته‌ای نداشته است
    rule = create_new_rule(3, 'T23', 'T2301P20', 'کاربر در یکسال گذشته هیچ تعامل سررسید گذشته‌ای نداشته است', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # B30DayDelayLast3-12M = 1	15	T2302P15	کاربر در یکسال گذشته 1 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T23', 'T2302P15', 'کاربر در یکسال گذشته 1 تعامل سررسید گذشته‌ داشته است', 1.94, 15, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2 <= B30DayDelayLast3-12M ≤ 3	05	T2303P5	کاربر در یکسال گذشته بین 2 تا 3 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T23', 'T2303P5', 'کاربر در یکسال گذشته بین 2 تا 3 تعامل سررسید گذشته‌ داشته است', 0.65, 5, 2, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 <= B30DayDelayLast3-12M ≤ 6	-10	T2304N10	کاربر در یکسال گذشته بین 4 تا 6 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T23', 'T2304N10', 'کاربر در یکسال گذشته بین 4 تا 6 تعامل سررسید گذشته‌ داشته است', 1.30, -10, 4, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= B30DayDelayLast3-12M ≤ 10	-15	T2305N15	کاربر در یکسال گذشته بین 7 تا 10 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T23', 'T2305N15', 'کاربر در یکسال گذشته بین 7 تا 10 تعامل سررسید گذشته‌ داشته است', 1.94, -15, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # B30DayDelayLast3-12M >= 11	-20	T2306N20	کاربر در یکسال گذشته بیش از 10 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T23', 'T2306N20', 'کاربر در یکسال گذشته بیش از 10 تعامل سررسید گذشته‌ داشته است', 2.59, -20, 11,
                           rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) done_past_due_trades_between_last_3_to_12_months_t23 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T23_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS})
    change_reason = create_new_score_reason(T23_RULES_DONE_PAST_DUE_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rule_codes, 'کاهش تعداد معاملات سررسید گذشته خاتمه یافته در یک سال گذشته', 'افزایش تعداد معاملات سررسید گذشته خاتمه یافته در یک سال گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) done_past_due_trades_between_last_3_to_12_months_t23 change reasons are created.')


def import_rules_timeliness_done_arrear_trades_of_last_3_months_t24(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T24', 'تعداد تعاملات معوق (بیش از 30 روز تاخیر) خاتمه یافته در ۳ ماه گذشته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # A30DayDelayLast3M = 0	20	T2401P20	کاربر در سه ماه گذشته هیچ تعامل معوقی نداشته است
    rule = create_new_rule(3, 'T24', 'T2401P20', 'کاربر در سه ماه گذشته هیچ تعامل معوقی نداشته است', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # A30DayDelayLast3M = 1	00	T2402P0	کاربر در سه ماه گذشته 1 تعامل معوق داشته است
    rule = create_new_rule(3, 'T24', 'T2402P0', 'کاربر در سه ماه گذشته 1 تعامل معوق داشته است', 0, 0, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2 <= A30DayDelayLast3M ≤ 3	-10	T2403N10	کاربر در سه ماه گذشته بین 2 تا 3 تعامل معوق داشته است
    rule = create_new_rule(3, 'T24', 'T2403N10', 'کاربر در سه ماه گذشته بین 2 تا 3 تعامل معوق داشته است', 1.30, -10, 2, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 <= A30DayDelayLast3M ≤ 6	-20	T2404N20	کاربر در سه ماه گذشته بین 4 تا 6 تعامل معوق داشته است
    rule = create_new_rule(3, 'T24', 'T2404N20', 'کاربر در سه ماه گذشته بین 4 تا 6 تعامل معوق داشته است', 2.59, -20, 4, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= A30DayDelayLast3M ≤ 10	-30	T2405N30	کاربر در سه ماه گذشته بین 7 تا 10 تعامل معوق داشته است
    rule = create_new_rule(3, 'T24', 'T2405N30', 'کاربر در سه ماه گذشته بین 7 تا 10 تعامل معوق داشته است', 3.89, -30, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 11 <= A30DayDelayLast3M <= 999 -40 T2406N40	کاربر در سه ماه گذشته بیش از 10 تعامل معوق داشته است
    rule = create_new_rule(3, 'T24', 'T2406N40', 'کاربر در سه ماه گذشته بیش از 10 تعامل معوق داشته است', 5.19, -40, 11, 999)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) done_arrear_trades_of_last_3_months_t24 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T24_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS})
    change_reason = create_new_score_reason(T24_RULES_DONE_ARREAR_TRADES_OF_LAST_3_MONTHS, rule_codes, 'کاهش تعداد معاملات معوق خاتمه یافته در سه ماه گذشته', 'افزایش تعداد معاملات معوق خاتمه یافته در سه ماه گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) done_arrear_trades_of_last_3_months_t24 change reasons are created.')


def import_rules_timeliness_done_arrear_trades_between_last_3_to_12_months_t25(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T25', 'تعداد تعاملات معوق (بیش از 30 روز تاخیر) خاتمه یافته در ۳ تا ۱۲ ماه گذشته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # 0 <= A30DayDelay3-12M <= 0  20	T2501P20	کاربر در یکسال گذشته هیچ تعامل معوقی نداشته است
    rule = create_new_rule(3, 'T25', 'T2501P20', 'کاربر در یکسال گذشته هیچ تعامل معوقی نداشته است', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 1 <= A30DayDelay3-12M <= 1  05	T2502P5 	کاربر در یکسال گذشته 1 تعامل معوق داشته است
    rule = create_new_rule(3, 'T25', 'T2502P5', 'کاربر در یکسال گذشته 1 تعامل معوق داشته است', 0.65, 5, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2 <= A30DayDelay3-12M ≤ 3	 -05	T2503N5 	کاربر در یکسال گذشته بین 2 تا 3 تعامل معوق داشته است
    rule = create_new_rule(3, 'T25', 'T2503N5', 'کاربر در یکسال گذشته بین 2 تا 3 تعامل معوق داشته است', 0.65, -5, 2, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 <= A30DayDelay3-12M ≤ 6	 -10	T2504N10	کاربر در یکسال گذشته بین 4 تا 6 تعامل معوق داشته است
    rule = create_new_rule(3, 'T25', 'T2504N10', 'کاربر در یکسال گذشته بین 4 تا 6 تعامل معوق داشته است', 1.30, -10, 4, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= A30DayDelay3-12M ≤ 10 -20	T2505N20	کاربر در یکسال گذشته بین 7 تا 10 تعامل معوق داشته است
    rule = create_new_rule(3, 'T25', 'T2505N20', 'کاربر در یکسال گذشته بین 7 تا 10 تعامل معوق داشته است', 2.59, -20, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 11 <= A30DayDelay3-12M <= 999	-30	T2506N30	کاربر در یکسال گذشته بیش از 10 تعامل معوق داشته است
    rule = create_new_rule(3, 'T25', 'T2506N30', 'کاربر در یکسال گذشته 10 تعامل معوق داشته است', 3.89, -30, 11, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) arrear_trades_between_last_3_to_12_months_t25 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T25_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS})
    change_reason = create_new_score_reason(T25_RULES_DONE_ARREAR_TRADES_BETWEEN_LAST_3_TO_12_MONTHS, rule_codes, 'کاهش تعداد معاملات معوق خاتمه یافته در یک سال گذشته', 'افزایش تعداد معاملات معوق خاتمه یافته در یک سال گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) arrear_trades_between_last_3_to_12_months_t25 change reasons are created.')


def import_rules_timeliness_undone_past_due_trades_counts_t26(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T26', 'تعداد تعاملات سررسید گذشته (کمتر از 30 روز تاخیر) خاتمه نیافته', 1.30, 10)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # UnfinishedB30DayDelay = 0	10	T2601P10	کاربر در سه ماه گذشته هیچ تعامل سررسید گذشته‌ای نداشته است
    rule = create_new_rule(3, 'T26', 'T2601P10', 'کاربر در سه ماه گذشته هیچ تعامل سررسید گذشته‌ای نداشته است', 1.30, 10, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # UnfinishedB30DayDelay = 1	-20	T2602N20	کاربر در سه ماه گذشته یک تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T26', 'T2602N20', 'کاربر در سه ماه گذشته یک تعامل سررسید گذشته‌ داشته است', 2.59, -20, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2 <= UnfinishedB30DayDelay ≤ 3	-30	T2603N30	کاربر در سه ماه گذشته بین ۲ تا 3 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T26', 'T2603N30', 'کاربر در سه ماه گذشته بین ۲ تا 3 تعامل سررسید گذشته‌ داشته است', 3.89, -30, 2, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 <= UnfinishedB30DayDelay ≤ 6	-40	T2604N40	کاربر در سه ماه گذشته بین ۴ تا 6 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T26', 'T2604N40', 'کاربر در سه ماه گذشته بین ۴ تا 6 تعامل سررسید گذشته‌ داشته است', 5.19, -40, 4, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= UnfinishedB30DayDelay ≤ 10	-50	T2605N50	کاربر در سه ماه گذشته بین ۷ تا 10 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T26', 'T2605N50', 'کاربر در سه ماه گذشته بین ۷ تا 10 تعامل سررسید گذشته‌ داشته است', 6.48, -50, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # UnfinishedB30DayDelay >= 11	-60	T2606N60	کاربر در سه ماه گذشته بیش از 10 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T26', 'T2606N60', 'کاربر در سه ماه گذشته بیش از 10 تعامل سررسید گذشته‌ داشته است', 7.78, -60, 11,
                           rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) timeliness_undone_past_due_trades_counts_t26 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T26_RULES_UNDONE_PAST_DUE_TRADES_COUNTS})
    change_reason = create_new_score_reason(T26_RULES_UNDONE_PAST_DUE_TRADES_COUNTS, rule_codes, 'کاهش تعداد معاملات سررسید گذشته خاتمه نیافته در سه ماه گذشته', 'افزایش تعداد معاملات سررسید گذشته خاتمه نیافته در سه ماه گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) timeliness_undone_past_due_trades_counts_t26 change reasons are created.')


def import_rules_timeliness_undone_arrear_trades_counts_t27(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T27', 'تعداد تعاملات معوق (بیش از 30 روز تاخیر) خاتمه نیافته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # UnfinishedA30DayDelay = 0	20	T2701P20	کاربر در سه ماه گذشته هیچ تعامل سررسید گذشته‌ای نداشته است
    rule = create_new_rule(3, 'T27', 'T2701P20', 'کاربر در سه ماه گذشته هیچ تعامل سررسید گذشته‌ای نداشته است', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # UnfinishedA30DayDelay = 1	-20	T2702N20	کاربر در سه ماه گذشته یک سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T27', 'T2702N20', 'کاربر در سه ماه گذشته یک سررسید گذشته‌ داشته است', 2.59, -20, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2 <= UnfinishedA30DayDelay ≤ 3	-30	T2703N30	کاربر در سه ماه گذشته بین 2 تا 3 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T27', 'T2703N30', 'کاربر در سه ماه گذشته بین 2 تا 3 تعامل سررسید گذشته‌ داشته است', 3.89, -30, 2, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 <= UnfinishedA30DayDelay ≤ 6	-40	T2704N40	کاربر در سه ماه گذشته بین 4 تا 6 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T27', 'T2704N40', 'کاربر در سه ماه گذشته بین 4 تا 6 تعامل سررسید گذشته‌ داشته است', 5.19, -40, 4, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= UnfinishedA30DayDelay ≤ 10	-50	T2705N50	کاربر در سه ماه گذشته بین 7 تا 10 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T27', 'T2705N50', 'کاربر در سه ماه گذشته بین 7 تا 10 تعامل سررسید گذشته‌ داشته است', 6.48, -50, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # UnfinishedA30DayDelay >= 11	-60	T2706N60	کاربر در سه ماه گذشته بیش از 10 تعامل سررسید گذشته‌ داشته است
    rule = create_new_rule(3, 'T27', 'T2706N60', 'کاربر در سه ماه گذشته بیش از 10 تعامل سررسید گذشته‌ داشته است', 7.78, -60, 11,
                           rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) undone_arrear_trades_counts_t27 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T27_RULES_UNDONE_ARREAR_TRADES_COUNTS})
    change_reason = create_new_score_reason(T27_RULES_UNDONE_ARREAR_TRADES_COUNTS, rule_codes, 'کاهش تعداد معاملات معوق خاتمه نیافته در سه ماه گذشته', 'افزایش تعداد معاملات معوق خاتمه نیافته در سه ماه گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) undone_arrear_trades_counts_t27 change reasons are created.')


def import_rules_timeliness_done_trades_average_delay_days_ratios_t28(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T28', 'نسبت میانگین تاخیر تعاملات کاربر به میانگین تاخیر سایر کاربران', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # AverageDelayRatio = 0	20	T2801P20	کاربر در انجام تعاملات تاخیر نداشته است
    rule = create_new_rule(3, 'T28', 'T2801P20', 'کاربر در انجام تعاملات تاخیر نداشته است', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= AverageDelayRatio ≤ 0.5	10	T2802P10	نسبت بین 0.001 و 0.5 می‌باشد
    rule = create_new_rule(3, 'T28', 'T2802P10', 'نسبت بین 0.001 و 0.5 می‌باشد', 1.30, 10, 0.001, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.501 <= AverageDelayRatio ≤ 1	00	T2803P0	نسبت بین 0.501 و 1 می‌باشد
    rule = create_new_rule(3, 'T28', 'T2803P0', 'نسبت بین 0.501 و 1 می‌باشد', 0, 0, 0.501, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.001 <= AverageDelayRatio ≤ 1.5	-10	T2804N10	نسبت بین 1.001 و 1.5 می‌باشد
    rule = create_new_rule(3, 'T28', 'T2804N10', 'نسبت بین 1.001 و 1.5 می‌باشد', 1.30, -10, 1.001, 1.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.501 <= AverageDelayRatio ≤ 2	-20	T2805N20	نسبت بین 1.501 و 2 می‌باشد
    rule = create_new_rule(3, 'T28', 'T2805N20', 'نسبت بین 1.501 و 2 می‌باشد', 2.59, -20, 1.501, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # AverageDelayRatio >= 2.001	-30	T2806N30	نسبت بیش از 2 می‌باشد
    rule = create_new_rule(3, 'T28', 'T2806N30', 'نسبت بیش از 2 می‌باشد', 3.89, -30, 2.001, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) done_trades_average_delay_days_ratios_t28 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T28_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS})
    change_reason = create_new_score_reason(T28_RULES_DONE_TRADES_AVERAGE_DELAY_DAYS, rule_codes, 'کاهش تاخیر کاربر در انجام معاملات نسبت به سایر کاربران', 'افزایش تاخیر کاربر در انجام معاملات نسبت به سایر کاربران')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) done_trades_average_delay_days_ratios_t28 change reasons are created.')


def import_rules_timeliness_unfixed_returned_cheques_count_of_last_3_months_t29(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T29', 'تعداد چک‌های برگشتی رفع سو اثر نشده در  ۳ ماه گذشته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # DishonouredChequesL3M = 0	20	T2901P20	کاربر چک برگشتی ندارد
    rule = create_new_rule(3, 'T29', 'T2901P20', 'کاربر چک برگشتی ندارد', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # DishonouredChequesL3M = 1	-10	T2902N10	کاربر ۱ چک برگشتی دارد
    rule = create_new_rule(3, 'T29', 'T2902N10', 'کاربر ۱ چک برگشتی دارد', 1.30, -10, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesL3M = 2	-20	T2903N20	کاربر ۲ چک برگشتی دارد
    rule = create_new_rule(3, 'T29', 'T2903N20', 'کاربر 2 چک برگشتی دارد', 2.59, -20, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesL3M = 3	-30	T2904N30	کاربر ۳ چک برگشتی دارد
    rule = create_new_rule(3, 'T29', 'T2904N30', 'کاربر 3 چک برگشتی دارد', 3.89, -30, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesL3M > 3	-40	T2905N40	کاربر بیش از ۳ چک برگشتی دارد
    rule = create_new_rule(3, 'T29', 'T2905N40', 'کاربر بیش از ۳ چک برگشتی دارد', 5.19, -40, 4, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) unfixed_returned_cheques_count_of_last_3_months_t29 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T29_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_LAST_3_MONTHS})
    change_reason = create_new_score_reason(T29_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_LAST_3_MONTHS, rule_codes, 'کاهش تعداد چک‌های برگشتی رفع سو اثر نشده در سه ماه گذشته', 'افزایش تعداد چک‌های برگشتی رفع سو اثر نشده در سه ماه گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) unfixed_returned_cheques_count_of_last_3_months_t29 rules are created.')


def import_rules_timeliness_unfixed_returned_cheques_count_between_last_3_to_12_months_t30(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T30', 'تعداد چک‌های برگشتی رفع سو اثر نشده در بازه ۳ تا ۱۲ ماه گذشته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # DishonouredChequesL3-12M = 0	20	T3001P20	کاربر چک برگشتی ندارد
    rule = create_new_rule(3, 'T30', 'T3001P20', 'کاربر چک برگشتی ندارد', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # DishonouredChequesL3-12M = 1	-10	T3002N30	کاربر ۱ چک برگشتی دارد
    rule = create_new_rule(3, 'T30', 'T3002N30', 'کاربر ۱ چک برگشتی دارد', 3.89, -30, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesL3-12M = 2	-20	T3003N40	کاربر ۲ چک برگشتی دارد
    rule = create_new_rule(3, 'T30', 'T3003N40', 'کاربر 2 چک برگشتی دارد', 5.19, -40, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesL3-12M = 3	-30	T3004N50	کاربر ۳ چک برگشتی دارد
    rule = create_new_rule(3, 'T30', 'T3004N50', 'کاربر 3 چک برگشتی دارد', 6.48, -50, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesL3-12M > 3	-40	T3005N60	کاربر بیش از ۳ چک برگشتی دارد
    rule = create_new_rule(3, 'T30', 'T3005N60', 'کاربر بیش از ۳ چک برگشتی دارد', 7.78, -60, 4, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) unfixed_returned_cheques_count_between_last_3_to_12_months_t30 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T30_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_BETWEEN_LAST_3_TO_12_MONTHS})
    change_reason = create_new_score_reason(T30_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_BETWEEN_LAST_3_TO_12_MONTHS, rule_codes, 'کاهش تعداد چک‌های برگشتی رفع سو اثر نشده در یک سال گذشته', 'افزایش تعداد چک‌های برگشتی رفع سو اثر نشده در یک سال گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) unfixed_returned_cheques_count_between_last_3_to_12_months_t30 change reasons are created.')


def import_rules_timeliness_unfixed_returned_cheques_count_of_more_12_months_t31(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T31', 'تعداد چک‌های برگشتی رفع سو اثر نشده در بیش از ۱۲ ماه گذشته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # DishonouredChequesA12M = 0	20	T3101P20	کاربر چک برگشتی ندارد
    rule = create_new_rule(3, 'T31', 'T3101P20', 'کاربر چک برگشتی ندارد', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # DishonouredChequesA12M = 1	-40	T3102N40	کاربر ۱ چک برگشتی دارد
    rule = create_new_rule(3, 'T31', 'T3102N40', 'کاربر ۱ چک برگشتی دارد', 5.19, -40, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesA12M = 2	-50	T3103N50	کاربر ۲ چک برگشتی دارد
    rule = create_new_rule(3, 'T31', 'T3103N50', 'کاربر ۲ چک برگشتی دارد', 6.48, -50, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesA12M = 3	-60	T3104N60	کاربر ۳ چک برگشتی دارد
    rule = create_new_rule(3, 'T31', 'T3104N60', 'کاربر ۳ چک برگشتی دارد', 7.78, -60, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredChequesA12M >= 4	-70	T3105N70	کاربر بیش از ۳ چک برگشتی دارد
    rule = create_new_rule(3, 'T31', 'T3105N70', 'کاربر بیش از ۳ چک برگشتی دارد', 9.07, -70, 4, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) unfixed_returned_cheques_count_of_more_12_months_t31 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T31_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_MORE_12_MONTHS})
    change_reason = create_new_score_reason(T31_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_MORE_12_MONTHS, rule_codes, 'کاهش تعداد چک‌های برگشتی رفع سو اثر نشده در بیش از یک سال گذشته', 'افزایش تعداد چک‌های برگشتی رفع سو اثر نشده در بیش از یک سال گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) unfixed_returned_cheques_count_of_more_12_months_t31 change reasons are created.')


def import_rules_timeliness_unfixed_returned_cheques_count_of_last_5_years_t32(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T32', 'تعداد کل چک‌های برگشتی رفع سو اثر شده در 5 سال گذشته', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # AllDishonouredCheques = 0	20	T3201P20	کاربر چک برگشتی ندارد
    rule = create_new_rule(3, 'T32', 'T3201P20', 'کاربر چک برگشتی ندارد', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    #  1 ≤ AllDishonouredCheques ≤ 3	00	T3202P0	کاربر بین 1 تا 3 چک برگشتی دارد
    rule = create_new_rule(3, 'T32', 'T3202P0', 'کاربر بین 1 تا 3 چک برگشتی دارد', 0, 0, 1, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 4 <= AllDishonouredCheques ≤ 6	-10	T3203N10	کاربر بین 4 تا 6 چک برگشتی دارد
    rule = create_new_rule(3, 'T32', 'T3203N10', 'کاربر بین 4 تا 6 چک برگشتی دارد', 1.30, -10, 4, 6)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 7 <= AllDishonouredCheques ≤ 10	-20	T3204N20	کاربر کاربر بین 7 تا 10 چک برگشتی دارد
    rule = create_new_rule(3, 'T32', 'T3204N20', 'کاربر کاربر بین 7 تا 10 چک برگشتی دارد', 2.59, -20, 7, 10)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DishonouredCheques >= 11	-30	T3205N30	کاربر بیش از 10 چک برگشتی دارد
    rule = create_new_rule(3, 'T32', 'T3205N30', 'کاربر بیش از 10 چک برگشتی دارد', 3.89, -30, 11, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) unfixed_returned_cheques_count_of_last_5_years_t32 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T32_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_LAST_5_YEARS})
    change_reason = create_new_score_reason(T32_RULES_CHEQUE_UNFIXED_RETURNED_COUNT_OF_LAST_5_YEARS, rule_codes, 'کاهش تعداد چک‌های برگشتی رفع سو اثر شده در پنج سال گذشته', 'افزایش تعداد چک‌های برگشتی رفع سو اثر شده در پنج سال گذشته')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) unfixed_returned_cheques_count_of_last_5_years_t32 change reasons are created.')


def import_rules_timeliness_past_due_loans_total_count_t33(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T33', 'تعداد تسهیلات سررسید گذشته در جریان', 1.30, 10)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # PastDueLoans = 0	10	T3301P10	کاربر تسهیلات سررسید گذشته ندارد
    rule = create_new_rule(3, 'T33', 'T3301P10', 'کاربر تسهیلات سررسید گذشته ندارد', 1.30, 10, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # PastDueLoans = 1	00	T3302P0	کاربر 1 تسهیلات سررسید گذشته دارد
    rule = create_new_rule(3, 'T33', 'T3302P0', 'کاربر 1 تسهیلات سررسید گذشته دارد', 0, 0, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # PastDueLoans = 2	-10	T3303N10	کاربر ۲ تسهیلات سررسید گذشته دارد
    rule = create_new_rule(3, 'T33', 'T3303N10', 'کاربر ۲ تسهیلات سررسید گذشته دارد', 1.30, -10, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # PastDueLoans = 3	-20	T3304N20	کاربر ۳ تسهیلات سررسید گذشته دارد
    rule = create_new_rule(3, 'T33', 'T3304N20', 'کاربر ۳ تسهیلات سررسید گذشته دارد', 2.59, -20, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # PastDueLoans >= 4	-30	T3305N30	کاربر بیش از ۳ تسهیلات سررسید گذشته دارد
    rule = create_new_rule(3, 'T33', 'T3305N30', 'کاربر بیش از ۳ تسهیلات سررسید گذشته دارد', 3.89, -30, 4, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) past_due_loans_total_count_t33 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T33_RULES_LOAN_PAST_DUE_TOTAL_COUNTS})
    change_reason = create_new_score_reason(T33_RULES_LOAN_PAST_DUE_TOTAL_COUNTS, rule_codes, 'کاهش تعداد تسهیلات سررسید گذشته در جریان', 'افزایش تعداد تسهیلات سررسید گذشته در جریان')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) past_due_loans_total_count_t33 change reasons are created.')


def import_rules_timeliness_arrear_loans_total_count_t34(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T34', 'تعداد تسهیلات معوق در جریان', 2.59, 20)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # DelayedLoans = 0	20	T3401P20	کاربر تسهیلات معوق ندارد
    rule = create_new_rule(3, 'T34', 'T3401P20', 'کاربر تسهیلات معوق ندارد', 2.59, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # DelayedLoans = 1	-10	T3402N10	کاربر 1 تسهیلات معوق دارد
    rule = create_new_rule(3, 'T34', 'T3402N10', 'کاربر 1 تسهیلات معوق دارد', 1.30, -10, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DelayedLoans = 2	-20	T3403N20	کاربر ۲ تسهیلات معوق دارد
    rule = create_new_rule(3, 'T34', 'T3403N20', 'کاربر ۲ تسهیلات معوق دارد', 2.59, -20, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DelayedLoans = 3	-30	T3404N30	کاربر ۳ تسهیلات معوق دارد
    rule = create_new_rule(3, 'T34', 'T3404N30', 'کاربر ۳ تسهیلات معوق دارد', 3.89, -30, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DelayedLoans >= 4	-40	T3405N40	کاربر بیش از ۳ تسهیلات معوق دارد
    rule = create_new_rule(3, 'T34', 'T3405N40', 'کاربر بیش از ۳ تسهیلات معوق دارد', 5.19, -40, 4, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) arrear_loans_total_count_t34 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T34_RULES_LOAN_ARREAR_TOTAL_COUNTS})
    change_reason = create_new_score_reason(T34_RULES_LOAN_ARREAR_TOTAL_COUNTS, rule_codes, 'کاهش تعداد تسهیلات معوق در جریان', 'افزایش تعداد تسهیلات معوق در جریان')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) arrear_loans_total_count_t34 change reasons are created.')


def import_rules_timeliness_suspicious_loans_total_count_t35(ds: DataService):
    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months master: level 2
    rule = create_new_rule(2, 'T', 'T35', 'تعداد تسهیلات مشکوک الوصول در جریان', 3.89, 30)
    ds.insert_rule(rule)

    # define Timeliness(T)' rules of done_arrear_trades_of_last_3_months details: level 3
    # DoubfulCollectionLoans = 0	30	T3501P30	کاربر تسهیلات مشکوک الوصول ندارد
    rule = create_new_rule(3, 'T35', 'T3501P30', 'کاربر تسهیلات مشکوک الوصول ندارد', 3.89, 30, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # DoubfulCollectionLoans = 1	-20	T3502N20	کاربر 1 تسهیلات مشکوک الوصول دارد
    rule = create_new_rule(3, 'T35', 'T3502N20', 'کاربر 1 تسهیلات مشکوک الوصول دارد', 2.59, -20, 1, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DoubfulCollectionLoans = 2	-30	T3503N30	کاربر ۲ تسهیلات مشکوک الوصول دارد
    rule = create_new_rule(3, 'T35', 'T3503N30', 'کاربر ۲ تسهیلات مشکوک الوصول دارد', 3.89, -30, 2, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DoubfulCollectionLoans = 3	-40	T3504N40	کاربر ۳ تسهیلات مشکوک الوصول دارد
    rule = create_new_rule(3, 'T35', 'T3504N40', 'کاربر ۳ تسهیلات مشکوک الوصول دارد', 5.19, -40, 3, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DoubfulCollectionLoans >= 4	-50	T3505N50	کاربر بیش از ۳ تسهیلات مشکوک الوصول دارد
    rule = create_new_rule(3, 'T35', 'T3505N50', 'کاربر بیش از ۳ تسهیلات مشکوک الوصول دارد', 6.48, -50, 4, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Timeliness(T) suspicious_loans_total_count_t35 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: T35_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS})
    change_reason = create_new_score_reason(T35_RULES_LOAN_SUSPICIOUS_TOTAL_COUNTS, rule_codes, 'کاهش تعداد تسهیلات مشکوک الوصول در جریان', 'افزایش تعداد تسهیلات مشکوک الوصول در جریان')
    ds.insert_score_reason(change_reason)
    print('Timeliness(T) suspicious_loans_total_count_t35 change reasons are created.')


def import_rules_timeliness(ds: DataService):
    import_rule_timeliness_master(ds)
    import_rules_timeliness_arrear_loans_total_count_t34(ds)
    import_rules_timeliness_done_arrear_trades_between_last_3_to_12_months_t25(ds)
    import_rules_timeliness_done_arrear_trades_of_last_3_months_t24(ds)
    import_rules_timeliness_done_past_due_trades_between_last_3_to_12_months_t23(ds)
    import_rules_timeliness_done_past_due_trades_of_last_3_months_t22(ds)
    import_rules_timeliness_done_trades_average_delay_days_ratios_t28(ds)
    import_rules_timeliness_past_due_loans_total_count_t33(ds)
    import_rules_timeliness_suspicious_loans_total_count_t35(ds)
    import_rules_timeliness_undone_arrear_trades_counts_t27(ds)
    import_rules_timeliness_undone_past_due_trades_counts_t26(ds)
    import_rules_timeliness_unfixed_returned_cheques_count_between_last_3_to_12_months_t30(ds)
    import_rules_timeliness_unfixed_returned_cheques_count_of_last_3_months_t29(ds)
    import_rules_timeliness_unfixed_returned_cheques_count_of_last_5_years_t32(ds)
    import_rules_timeliness_unfixed_returned_cheques_count_of_more_12_months_t31(ds)


if __name__ == '__main__':
    import_rules_timeliness(DataService(get_db()))
