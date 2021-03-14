from typing import List

from app.core.constants import rules_max_val, PARENT, VOLUMES, CODE, RULE_MASTER_CODE, V12_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, V13_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, \
    V14_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, V15_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, V16_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, V17_RULES_CHEQUE_UNFIXED_RETURNED_TOTAL_BALANCE_RATIOS, V18_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, \
    V21_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, V20_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, V19_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS
from app.core.database import get_db
from app.core.models.rules import Rule
from app.core.services.data_service import DataService
from app.core.services.util import create_new_rule, create_new_score_change_reason


# noinspection DuplicatedCode
def import_rule_volume_master(ds: DataService):
    # Delete all volumes(V) rules
    l2_rules: {Rule} = ds.get_rules({PARENT: VOLUMES})
    for r in l2_rules:
        # delete all l3_rules
        ds.delete_rules({PARENT: r[CODE]})

    # delete all l2_rules
    ds.delete_rules({PARENT: VOLUMES})
    # delete the l1_rule
    ds.delete_rules({CODE: VOLUMES})
    print('Volumes(V) rules are deleted.')

    # define Volume(V)' rules master: level 1
    rule = create_new_rule(1, None, 'V', 'حجم تعاملات', 25, 195)
    ds.insert_rule(rule)
    print('Volumes(V) master rule is created.')


def import_rules_volume_done_trades_total_balance_ratios_v12(ds: DataService):
    # define Volume(V)' rules of done_trades_total_balance_ratios master: level 2
    rule = create_new_rule(2, 'V', 'V12', 'نسبت مجموع کل مبالغ تعاملات موفق به میانگین مجموع مبالغ تعاملات موفق سایر کاربران', 6.41, 50)
    ds.insert_rule(rule)

    # define Volume(V)' rules of done_trades_total_balance_ratios details: level 3
    # SDealAmountRatio = 0	00	V1201P0	کاربر تعاملی نداشته است
    rule = create_new_rule(3, 'V12', 'V1201P0', 'کاربر تعاملی نداشته است', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= SDealAmountRatio ≤ 0.5	10	V1202P10	نسبت بین 0.001 و 0.5 می‌باشد
    rule = create_new_rule(3, 'V12', 'V1202P10', 'نسبت بین 0.001 و 0.5 می‌باشد', 1.28, 10, 0.001, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.501 <= SDealAmountRatio ≤ 1	20	V1203P20	نسبت بین 0.501 و 1 می‌باشد
    rule = create_new_rule(3, 'V12', 'V1203P20', 'نسبت بین 0.501 و 1 می‌باشد', 2.56, 20, 0.501, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.001 <= SDealAmountRatio ≤ 1.5	30	V1204P30	نسبت بین 1.001 و 1.5 می‌باشد
    rule = create_new_rule(3, 'V12', 'V1204P30', 'نسبت بین 1.001 و 1.5 می‌باشد', 3.85, 30, 1.001, 1.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.501 <= SDealAmountRatio ≤ 2	40	V1205P40	نسبت بین 1.501 و 2 می‌باشد  
    rule = create_new_rule(3, 'V12', 'V1205P40', 'نسبت بین 1.501 و 2 می‌باشد', 5.13, 40, 1.501, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # SDealAmountRatio >= 2.001	50	V1206P50	نسبت بیش از 2 می‌باشد  
    rule = create_new_rule(3, 'V12', 'V1206P50', 'نسبت بیش از 2 می‌باشد', 6.41, 50, 2.001, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) done_trades_total_balance_ratios_v12 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V12_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V12_RULES_DONE_TRADES_AVERAGE_TOTAL_BALANCE_RATIOS, rule_codes, 'افزایش نسبت مبالغ معاملات موفق به میانگین مبالغ معاملات سایر کاربران', 'کاهش نسبت مبالغ معاملات موفق به میانگین مبالغ معاملات سایر کاربران')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) done_trades_total_balance_ratios_v12 change reasons are created.')


def import_rules_volume_undone_past_due_trades_total_balance_of_last_year_ratios_v13(ds: DataService):
    # define Volume(V)' rules of undone_past_due_trades_total_balance_of_last_year_ratios master: level 2    
    rule = create_new_rule(2, 'V', 'V13',
                           'نسبت مجموع مبالغ تعاملات سررسید گذشته خاتمه ‌نیافته به مجموع مبالغ تعاملات موفق کاربر در یکسال گذشته', 2.56, 20)
    ds.insert_rule(rule)

    # define Volume(V)' rules of undone_past_due_trades_total_balance_of_last_year_ratios details: level 3
    # UnfinishedB30Din1YRatio = 0	20	V1301P20	کاربر تعامل سررسید گذشته خاتمه نیافته ندارد
    rule = create_new_rule(3, 'V13', 'V1301P20', ' تعامل سررسید گذشته خاتمه نیافته ندارد', 2.56, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= UnfinishedB30Din1YRatio ≤ 0.5	00	V1302P0	نسبت بین 0.001 و 0.5 می‌باشد
    rule = create_new_rule(3, 'V13', 'V1302P0', 'نسبت بین 0.001 و 0.5 می‌باشد', 0, 0, 0.001, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.5001 <= UnfinishedB30Din1YRatio ≤ 1	-10	V1303N10	نسبت بین 0.5001 و 1 می‌باشد
    rule = create_new_rule(3, 'V13', 'V1303N10', 'نسبت بین 0.5001 و 1 می‌باشد', 1.28, -10, 0.5001, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # todo: this rule is commented and handled its score by duplicating V1303N10 score
    # # If SDA (denominator) = 0	-20	V1304N20	کاربر در یکسال گذشته تعامل موفقی ندارد (اولین تعامل در حال انجام سررسید گذشته شده)
    # rule = RuleUnDonePastDueTradesTotalBalanceOfLastYearRatio()
    # # todo: should be checked, original val is: -20
    # rule.save(creat_rule(rule, 'V1304N20', 0, 0, -20, 'کاربر در یکسال گذشته تعامل موفقی ندارد (اولین تعامل در حال انجام سررسید گذشته شده)'))

    # 1 < UnfinishedB30Din1YRatio ≤ 1.5	-20	V1305N20	نسبت بین 1.001 و 1.5 می‌باشد
    rule = create_new_rule(3, 'V13', 'V1305N20', 'نسبت بین 1.001 و 1.5 می‌باشد', 2.56, -20, 1.001, 1.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.501 <= UnfinishedB30Din1YRatio ≤ 2	-30	V1306N30	نسبت بین 1.501 و 2 می‌باشد
    rule = create_new_rule(3, 'V13', 'V1306N30', 'نسبت بین 1.501 و 2 می‌باشد', 3.85, -30, 1.501, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # UnfinishedB30Din1YRatio > 2	-40	V1307N40	نسبت بیش از 2 می‌باشد
    rule = create_new_rule(3, 'V13', 'V1307N40', 'نسبت بیش از 2 می‌باشد', 5.13, -40, 3, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) undone_past_due_trades_total_balance_of_last_year_ratios_v13 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V13_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS})
    change_reason = create_new_score_change_reason(V13_RULES_UNDONE_PAST_DUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rule_codes, 'کاهش مبالغ معاملات سررسید گذشته خاتمه ‌نیافته', 'افزایش مبالغ معاملات سررسید گذشته خاتمه ‌نیافته')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) undone_past_due_trades_total_balance_of_last_year_ratios_v13 change reasons are created.')


def import_rules_volume_undone_arrear_trades_total_balance_of_last_year_ratios_v14(ds: DataService):
    # define Volume(V)' rules of undone_arrear_trades_total_balance_of_last_year_ratios master: level 2
    rule = create_new_rule(2, 'V', 'V14',
                           'نسبت مجموع مبالغ تعاملات معوق خاتمه ‌نیافته به مجموع مبالغ تعاملات موفق کاربر در یکسال گذشته', 3.85, 30)
    ds.insert_rule(rule)

    # define Volume(V)' rules of undone_arrear_trades_total_balance_of_last_year_ratios details: level 3
    # UnfinishedB30Din1YRatio = 0	30	V1401P30	کاربر تعامل معوق خاتمه نیافته ندارد
    rule = create_new_rule(3, 'V14', 'V1401P30', 'کاربر تعامل معوق خاتمه نیافته ندارد', 3.58, 30, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= UnfinishedB30Din1YRatio ≤ 0.5	00	V1402P0	نسبت بین 0.001 و 0.5 می‌باشد
    rule = create_new_rule(3, 'V14', 'V1402P0', 'نسبت بین 0.001 و 0.5 می‌باشد', 0, 0, 0.001, 0.5)
    ds.insert_rule(rule)

    # 0.5001 <= UnfinishedB30Din1YRatio ≤ 1	-10	V1403N10	نسبت بین 0.5001 و 1 می‌باشد
    rule = create_new_rule(3, 'V14', 'V1403N10', 'نسبت بین 0.5001 و 1 می‌باشد', 1.28, -10, 0.5001, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # todo: this rule is commented and handled its score by duplicating V1403N10 score
    # # If SDA (denominator) = 0	-20	V1404N20	کاربر در یکسال گذشته تعامل موفقی ندارد (اولین تعامل در حال انجام معوق است)
    # # todo: should be checked, original val is: -20
    # rule = RuleUnDoneArrearTradesTotalBalanceOfLastYearRatio()
    # rule.save(creat_rule(rule, 'V1404N20', 0, 0, 0, 'کاربر در یکسال گذشته تعامل موفقی ندارد (اولین تعامل در حال انجام معوق است)'))

    # 1 < UnfinishedB30Din1YRatio ≤ 1.5	-20	V1405N20	نسبت بین 1.001 و 1.5 می‌باشد
    rule = create_new_rule(3, 'V14', 'V1405N20', 'نسبت بین 1.001 و 1.5 می‌باشد', 2.56, -20, 1.001, 1.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.501 <= UnfinishedB30Din1YRatio ≤ 2	-30	V1406N30	نسبت بین 1.501 و 2 می‌باشد
    rule = create_new_rule(3, 'V14', 'V1406N30', 'نسبت بین 1.501 و 2 می‌باشد', 3.85, -30, 1.501, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # UnfinishedB30Din1YRatio > 2	-40	V1407N40	نسبت بیش از 2 می‌باشد
    rule = create_new_rule(3, 'V14', 'V1407N40', 'نسبت بیش از 2 می‌باشد', 5.13, -40, 3, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) undone_arrear_trades_total_balance_of_last_year_ratios_v14 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V14_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS})
    change_reason = create_new_score_change_reason(V14_RULES_UNDONE_ARREAR_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rule_codes, 'کاهش مبالغ معاملات معوق خاتمه ‌نیافته', 'افزایش مبالغ معاملات معوق خاتمه ‌نیافته')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) undone_arrear_trades_total_balance_of_last_year_ratios_v14 change reasons are created.')


def import_rules_volume_undone_undue_trades_total_balance_of_last_year_ratios_v15(ds: DataService):
    # define Volume(V)' rules of undone_arrear_trades_total_balance_of_last_year_ratios master: level 2
    rule = create_new_rule(2, 'V', 'V15',
                           'نسبت مجموع مبالغ تعاملات جاری سررسیدنشده به مجموع مبالغ تعاملات موفق کاربر در یکسال گذشته', 0, 0)
    ds.insert_rule(rule)

    # define Volume(V)' rules of undone_arrear_trades_total_balance_of_last_year_ratios details: level 3
    # If SDA(denominator) = 0	00	V1501P0	کاربر در یکسال گذشته تعامل موفقی ندارد (اولین تعامل در حال انجام است)
    rule = create_new_rule(3, 'V15', 'V1501P0', 'کاربر در یکسال گذشته تعامل موفقی ندارد (اولین تعامل در حال انجام است)', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 ≤ NotDueDealAmountRatio ≤ 1	-2	V1502N2	نسبت بین 0 و ۱ می‌باشد
    rule = create_new_rule(3, 'V15', 'V1502N2', 'نسبت بین 0 و ۱ می‌باشد', -0.26, -2, 0.001, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.001 < NotDueDealAmountRatio ≤ 1.5	-05	V1503N5	نسبت بین 1 و 1.5 می‌باشد
    rule = create_new_rule(3, 'V15', 'V1503N5', 'نسبت بین 1 و 1.5 می‌باشد', 0.64, -5, 1.001, 1.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.501 <= NotDueDealAmountRatio ≤ 2	-10	V1504N10	نسبت بین 1.5 و ۲ می‌باشد
    rule = create_new_rule(3, 'V15', 'V1504N10', 'نسبت بین 1.5 و ۲ می‌باشد', 1.28, -10, 1.501, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 2.001 <= NotDueDealAmountRatio ≤ 3	-20	V1505N20	نسبت بین ۲ و ۳ می‌باشد
    rule = create_new_rule(3, 'V15', 'V1505N20', 'نسبت بین ۲ و ۳ می‌باشد', 2.56, 20, 2.001, 3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # NotDueDealAmountRatio > 3	-30	V1506N30	نسبت بیش از ۳ می‌باشد
    rule = create_new_rule(3, 'V15', 'V1506N30', 'نسبت بیش از ۳ می‌باشد', 3.85, -30, 3.001, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) undone_undue_trades_total_balance_of_last_year_ratios_v15 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V15_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS})
    change_reason = create_new_score_change_reason(V15_RULES_UNDONE_UNDUE_TRADES_TOTAL_BALANCE_OF_LAST_YEAR_RATIOS, rule_codes, 'کاهش نسبت مبالغ معاملات جاری به مجموع مبالغ معاملات موفق', 'افزایش نسبت مبالغ معاملات جاری به مجموع مبالغ معاملات موفق')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) undone_undue_trades_total_balance_of_last_year_ratios_v15 change reasons are created.')


def import_rules_volume_loan_monthly_installments_total_balance_ratio_v16(ds: DataService):
    # define Volume(V)' rules of loan_monthly_installments_total_balance_ratio master: level 2
    rule = create_new_rule(2, 'V', 'V16',
                           'نسبت مجموع مبالغ اقساط ماهانه کاربر به میانگین مجموع مبالغ اقساط ماهانه سایر کاربران (تعاملات و تسهیلات)', 2.56, 20)
    ds.insert_rule(rule)

    # define Volume(V)' rules of loan_monthly_installments_total_balance_ratio details: level 3
    # MonthlyInstallments = 0	00	V1601P0	کاربر پرداخت اقساط ندارد
    rule = create_new_rule(3, 'V16', 'V1601P0', 'کاربر پرداخت اقساط ندارد', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= MonthlyInstallments ≤ 0.5	10	V1602P10	نسبت بین 0.001 و 0.5 می‌باشد
    rule = create_new_rule(3, 'V16', 'V1602P10', 'نسبت بین 0.001 و 0.5 می‌باشد', 1.28, 10, 0.001, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.501 <= MonthlyInstallments ≤ 1	20	V1603P20	نسبت بین 0.501 و 1 می‌باشد
    rule = create_new_rule(3, 'V16', 'V1603P20', 'نسبت بین 0.501 و 1 می‌باشد', 2.56, 20, 0.501, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V16_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V16_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, rule_codes, 'افزایش امکان سنجش رفتار اعتباری کاربر از طریق اقساط پرداختی', 'کاهش امکان سنجش رفتار اعتباری کاربر از طریق اقساط پرداختی')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) loan_monthly_installments_total_balance_ratio_v16 part-1 change reasons are created.')

    # 1.001 <= MonthlyInstallments ≤ 1.2	-2	V1604N2	نسبت بین 1.001 و 1.2 می‌باشد
    rule = create_new_rule(3, 'V16', 'V1604N2', 'نسبت بین 1.001 و 1.2 می‌باشد', 0.26, -2, 1.001, 1.2)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 1.201 <= MonthlyInstallments ≤ 2	-10	V1605N10	نسبت بین 1.201 و 2 می‌باشد
    rule = create_new_rule(3, 'V16', 'V1605N10', 'نسبت بین 1.201 و 2 می‌باشد', 1.28, -10, 1.201, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # MonthlyInstallments >= 2.001	-20	V1606N20	نسبت بیش از 2 می‌باشد
    rule = create_new_rule(3, 'V16', 'V1606N20', 'نسبت بیش از 2 می‌باشد', 2.56, -20, 2.001, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) loan_monthly_installments_total_balance_ratio_v16 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V16_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V16_RULES_LOAN_MONTHLY_INSTALLMENTS_TOTAL_BALANCE_RATIOS, rule_codes, 'کاهش نسبت مبالغ اقساط ماهانه کاربر به میانگین اقساط ماهانه سایر کاربران', 'افزایش نسبت مبالغ اقساط ماهانه کاربر به میانگین اقساط ماهانه سایر کاربران')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) loan_monthly_installments_total_balance_ratio_v16 part-2 change reasons are created.')


def import_rules_volume_unfixed_returned_cheques_total_balance_ratio_v17(ds: DataService):
    # define Volume(V)' rules of unfixed_returned_cheques_total_balance_ratio master: level 2
    rule = create_new_rule(2, 'V', 'V17',
                           'نسبت مجموع کل مبالغ چک‌های برگشتی رفع سو اثر نشده به میانگین مجموع مبالغ چک‌های برگشتی رفع سو اثر نشده سایر کاربران',
                           2.56, 20)
    ds.insert_rule(rule)

    # define Volume(V)' rules of unfixed_returned_cheques_total_balance_ratio details: level 3
    # DCAmountRatio = 0	20	V1701P20	کاربر چک برگشتی رفع سو اثر نشده ندارد
    rule = create_new_rule(3, 'V17', 'V1701P20', 'کاربر چک برگشتی رفع سو اثر نشده ندارد', 2.56, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= DCAmountRatio ≤ 0.5	00	V1702P0	نسبت بین 0.001 و 0.5 می‌باشد

    rule = create_new_rule(3, 'V17', 'V1702P0', 'نسبت بین 0.001 و 0.5 می‌باشد', 0, 0, 0.001, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.501 <= DCAmountRatio ≤ 1	-10	V1703N10	نسبت بین 0.501 و 1 می‌باشد
    rule = create_new_rule(3, 'V17', 'V1703N10', 'نسبت بین 0.501 و 1 می‌باشد', 1.28, -10, 0.501, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.001 <= DCAmountRatio ≤ 1.5	-20	V1704N20	نسبت بین 1.001 و 1.5 می‌باشد
    rule = create_new_rule(3, 'V17', 'V1704N20', 'نسبت بین 1.001 و 1.5 می‌باشد', 2.56, -20, 1.001, 1.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 1.501 <= DCAmountRatio ≤ 2	-30	V1705N30	نسبت بین 1.501 و 2 می‌باشد
    rule = create_new_rule(3, 'V17', 'V1705N30', 'نسبت بین 1.501 و 2 می‌باشد', 3.85, -30, 1.501, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DCAmountRatio >= 2.001	-40	V1706N40	نسبت بیش از 2 می‌باشد
    rule = create_new_rule(3, 'V17', 'V1706N40', 'نسبت بیش از 2 می‌باشد', 5.13, -40, 2.001, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) unfixed_returned_cheques_total_balance_ratio_v17 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V17_RULES_CHEQUE_UNFIXED_RETURNED_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V17_RULES_CHEQUE_UNFIXED_RETURNED_TOTAL_BALANCE_RATIOS, rule_codes, 'کاهش مبالغ چک‌های برگشتی رفع سو اثر نشده', 'افزایش مبالغ چک‌های برگشتی رفع سو اثر نشده')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) unfixed_returned_cheques_total_balance_ratio_v17 change reasons are created.')


def import_rules_volume_overdue_loans_total_balance_ratio_v18(ds: DataService):
    # define Volume(V)' rules of overdue_loans_total_balance_ratio master: level 2
    rule = create_new_rule(2, 'V', 'V18',
                           'نسبت مجموع کل مانده تسهیلات جاری به میانگین مجموع کل مانده تسهیلات جاری سایر کاربران',
                           1.28, 10)
    ds.insert_rule(rule)

    # define Volume(V)' rules of overdue_loans_total_balance_ratio details: level 3
    # CurrentLoanAmountRatio = 0	00	V1801P0	کاربر تسهیلات جاری ندارد
    rule = create_new_rule(3, 'V18', 'V1801P0', 'کاربر تسهیلات جاری ندارد', 0, 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= CurrentLoanAmountRatio ≤ 0.5	05	V1802P5	نسبت بین 0.001 و 0.5 می‌باشد
    rule = create_new_rule(3, 'V18', 'V1802P5', 'نسبت بین 0.001 و 0.5 می‌باشد', 0.64, 5, 0.001, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.501 <= CurrentLoanAmountRatio ≤ 1	10	V1803P10	نسبت بین 0.501 و 1 می‌باشد
    rule = create_new_rule(3, 'V18', 'V1803P10', 'نسبت بین 0.501 و 1 می‌باشد', 1.28, 10, 0.501, 1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V18_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V18_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, rule_codes, 'افزایش امکان سنجش رفتار اعتباری کاربر از طریق مانده جاری تسهیلات', 'کاهش امکان سنجش رفتار اعتباری کاربر از طریق مانده جاری تسهیلات')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) overdue_loans_total_balance_ratio_v18 part-1 change reasons are created.')

    # 1.001 <= CurrentLoanAmountRatio ≤ 1.5	-05	V1804N5	نسبت بین 1.001 و 1.5 می‌باشد
    rule = create_new_rule(3, 'V18', 'V1804N5', 'نسبت بین 1.001 و 1.5 می‌باشد', 0.64, -5, 1.001, 1.5)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 1.501 <= CurrentLoanAmountRatio ≤ 2	-10	V1805N10	نسبت بین 1.501 و 2 می‌باشد
    rule = create_new_rule(3, 'V18', 'V1805N10', 'نسبت بین 1.501 و 2 می‌باشد', 1.28, -10, 1.501, 2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # CurrentLoanAmountRatio >= 2.001	-20	V1806N20	نسبت بیش از 2 می‌باشد
    rule = create_new_rule(3, 'V18', 'V1806N20', 'نسبت بیش از 2 می‌باشد', 2.56, -20, 2.001, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) overdue_loans_total_balance_ratio_v18 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V18_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V18_RULES_LOAN_OVERDUE_TOTAL_BALANCE_RATIOS, rule_codes, '', '')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) overdue_loans_total_balance_ratio_v18 part-2 change reasons are created.')


def import_rules_volume_past_due_loans_total_balance_ratio_v19(ds: DataService):
    # define Volume(V)' rules of past_due_loans_total_balance_ratio master: level 2
    rule = create_new_rule(2, 'V', 'V19',
                           'نسبت مجموع کل مانده تسهیلات سررسیدگذشته به مجموع کل اصل و سود تسهیلات در جریان',
                           1.28, 10)
    ds.insert_rule(rule)

    # define Volume(V)' rules of past_due_loans_total_balance_ratio details: level 3
    # PastDueLoanAmountRatio = 0	10	V1901P10	کاربر تسهیلات سررسیدگذشته ندارد
    rule = create_new_rule(3, 'V19', 'V1901P10', 'کاربر تسهیلات سررسیدگذشته ندارد', 1.28, 10, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= PastDueLoanAmountRatio ≤ 0.1	-05	V1902N5	نسبت بین 0.001 و 0.1 می‌باشد
    rule = create_new_rule(3, 'V19', 'V1902N5', 'نسبت بین 0.001 و 0.1 می‌باشد', 0.64, -5, 0.001, 0.1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.101 <= PastDueLoanAmountRatio ≤ 0.2	-10	V1903N10	نسبت بین 0.101 و 0.2 می‌باشد
    rule = create_new_rule(3, 'V19', 'V1903N10', 'نسبت بین 0.101 و 0.2 می‌باشد', 1.28, -10, 0.101, 0.2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.201 <= PastDueLoanAmountRatio ≤ 0.3	-20	V1904N20	نسبت بین 0.201 و 0.3 می‌باشد
    rule = create_new_rule(3, 'V19', 'V1904N20', 'نسبت بین 0.201 و 0.3 می‌باشد', 2.56, -20, 0.201, 0.3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.301 <= PastDueLoanAmountRatio ≤ 0.5	-30	V1905N30	نسبت بین 0.301 و 0.5 می‌باشد
    rule = create_new_rule(3, 'V19', 'V1905N30', 'نسبت بین 0.301 و 0.5 می‌باشد', 3.85, -30, 0.301, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # PastDueLoanAmountRatio >= 0.501	-40	V1906N40	نسبت بیش از 0.5 می‌باشد
    rule = create_new_rule(3, 'V19', 'V1906N40', 'نسبت بیش از 0.5 می‌باشد', 5.13, -40, 0.501, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) past_due_loans_total_balance_ratio_v19 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V19_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V19_RULES_LOAN_PAST_DUE_TOTAL_BALANCE_RATIOS, rule_codes, 'کاهش نسبت مانده تسهیلات سررسیدگذشته به مجموع اصل و سود تسهیلات در جریان', 'افزایش نسبت مانده تسهیلات سررسیدگذشته به مجموع اصل و سود تسهیلات در جریان')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) past_due_loans_total_balance_ratio_v19 change reasons are created.')


def import_rules_volume_arrear_loans_total_balance_ratios_v20(ds: DataService):
    # define Volume(V)' rules of arrear_loans_total_balance_ratios master: level 2
    rule = create_new_rule(2, 'V', 'V20',
                           'نسبت مجموع کل مانده تسهیلات معوق به مجموع کل اصل و سود تسهیلات در جریان',
                           1.92, 15)
    ds.insert_rule(rule)

    # define Volume(V)' rules of arrear_loans_total_balance_ratios details: level 3
    # DelayedLoanAmountRatio = 0	15	V2001P15	کاربر تسهیلات معوق ندارد
    rule = create_new_rule(3, 'V20', 'V2001P15', 'کاربر تسهیلات معوق ندارد', 1.92, 15, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= DelayedLoanAmountRatio ≤ 0.1	-10	V2002N10	نسبت بین 0 و 0.1 می‌باشد
    rule = create_new_rule(3, 'V20', 'V2002N10', 'نسبت بین 0 و 0.1 می‌باشد', 1.28, -10, 0.001, 0.1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.101 <= DelayedLoanAmountRatio ≤ 0.2	-20	V2003N20	نسبت بین 0.101 و 0.2 می‌باشد
    rule = create_new_rule(3, 'V20', 'V2003N20', 'نسبت بین 0.101 و 0.2 می‌باشد', 2.56, -20, 0.101, 0.2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.201 <= DelayedLoanAmountRatio ≤ 0.3	-30	V2004N30	نسبت بین 0.201 و 0.3 می‌باشد
    rule = create_new_rule(3, 'V20', 'V2004N30', 'نسبت بین 0.201 و 0.3 می‌باشد', 3.85, -30, 0.201, 0.3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.301 <= DelayedLoanAmountRatio ≤ 0.5	-40	V2005N40	نسبت بین  0.301و 0.5 می‌باشد
    rule = create_new_rule(3, 'V20', 'V2005N40', 'نسبت بین  0.301و 0.5 می‌باشد', 5.13, -40, 0.301, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DelayedLoanAmountRatio >= 0.501	-50	V2006N50	نسبت بیش از 0.5 می‌باشد
    rule = create_new_rule(3, 'V20', 'V2006N50', 'نسبت بیش از 0.5 می‌باشد', 6.41, -50, 0.501, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) arrear_loans_total_balance_ratios_v20 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V20_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V20_RULES_LOAN_ARREAR_TOTAL_BALANCE_RATIOS, rule_codes, 'کاهش نسبت مانده تسهیلات معوق به مجموع اصل و سود تسهیلات در جریان', 'افزایش نسبت مانده تسهیلات معوق به مجموع اصل و سود تسهیلات در جریان')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) arrear_loans_total_balance_ratios_v20 change reasons are created.')


def import_rules_volume_suspicious_loans_total_balance_ratio_v21(ds: DataService):
    # define Volume(V)' rules of suspicious_loans_total_balance_ratio master: level 2
    rule = create_new_rule(2, 'V', 'V21',
                           'نسبت مجموع کل مانده تسهیلات مشکوک‌الوصول به مجموع کل اصل و سود تسهیلات در جریان',
                           2.56, 20)
    ds.insert_rule(rule)
    # define Volume(V)' rules of suspicious_loans_total_balance_ratio details: level 3
    # DoubtfulCollectionAmountRatio = 0	20	V2101P20	کاربر تسهیلات مشکوک‌الوصول ندارد

    rule = create_new_rule(3, 'V21', 'V2101P20', 'کاربر تسهیلات مشکوک‌الوصول ندارد', 2.56, 20, 0, 0)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # 0.001 <= DoubtfulCollectionAmountRatio ≤ 0.1	-20	V2102N20	نسبت بین 0.001 و 0.1 می‌باشد
    rule = create_new_rule(3, 'V21', 'V2102N20', 'نسبت بین 0.001 و 0.1 می‌باشد', 2.56, -20, 0.001, 0.1)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.101 <= DoubtfulCollectionAmountRatio ≤ 0.2	-30	V2103N30	نسبت بین 0.101 و 0.2 می‌باشد
    rule = create_new_rule(3, 'V21', 'V2103N30', 'نسبت بین 0.101 و 0.2 می‌باشد', 3.85, -30, 0.101, 0.2)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.201 <= DoubtfulCollectionAmountRatio ≤ 0.3	-40	V2104N40	نسبت بین 0.201 و 0.3 می‌باشد
    rule = create_new_rule(3, 'V21', 'V2104N40', 'نسبت بین 0.201 و 0.3 می‌باشد', 5.13, -40, 0.201, 0.3)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # 0.301 <= DoubtfulCollectionAmountRatio ≤ 0.5	-50	V2105N50	نسبت بین 0.301 و 0.5 می‌باشد
    rule = create_new_rule(3, 'V21', 'V2105N50', 'نسبت بین 0.301 و 0.5 می‌باشد', 6.41, -50, 0.301, 0.5)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # DoubtfulCollectionAmountRatio >= 0.501	-60	V2106N60	نسبت بیش از 0.5 می‌باشد
    rule = create_new_rule(3, 'V21', 'V2106N60', 'نسبت بیش از 0.5 می‌باشد', 7.69, -60, 0.501, rules_max_val)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Volumes(V) suspicious_loans_total_balance_ratio_v21 rules are created.')
    ds.delete_score_change_reasons({RULE_MASTER_CODE: V21_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS})
    change_reason = create_new_score_change_reason(V21_RULES_LOAN_SUSPICIOUS_TOTAL_BALANCE_RATIOS, rule_codes, 'کاهش نسبت مانده تسهیلات مشکوک‌الوصول به مجموع اصل و سود تسهیلات در جریان', 'افزایش نسبت مانده تسهیلات مشکوک‌الوصول به مجموع اصل و سود تسهیلات در جریان')
    ds.insert_score_change_reason(change_reason)
    print('Volumes(V) suspicious_loans_total_balance_ratio_v21 part-1 change reasons are created.')


def import_rules_volumes(ds: DataService):
    import_rule_volume_master(ds)
    import_rules_volume_done_trades_total_balance_ratios_v12(ds)
    import_rules_volume_undone_past_due_trades_total_balance_of_last_year_ratios_v13(ds)
    import_rules_volume_undone_arrear_trades_total_balance_of_last_year_ratios_v14(ds)
    import_rules_volume_undone_undue_trades_total_balance_of_last_year_ratios_v15(ds)
    import_rules_volume_loan_monthly_installments_total_balance_ratio_v16(ds)
    import_rules_volume_unfixed_returned_cheques_total_balance_ratio_v17(ds)
    import_rules_volume_overdue_loans_total_balance_ratio_v18(ds)
    import_rules_volume_past_due_loans_total_balance_ratio_v19(ds)
    import_rules_volume_arrear_loans_total_balance_ratios_v20(ds)
    import_rules_volume_suspicious_loans_total_balance_ratio_v21(ds)


if __name__ == '__main__':
    import_rules_volumes(DataService(get_db()))
