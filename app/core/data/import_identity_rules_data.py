from typing import List

from app.core.constants import PARENT, IDENTITIES, CODE, I2_RULES_PROFILE_MILITARY_SERVICE_STATUS, I3_RULES_PROFILE_SIM_CARD_OWNERSHIPS, I4_RULES_PROFILE_ADDRESS_VERIFICATIONS, RULE_MASTER_CODE, I1_RULES_PROFILE_HAS_KYCS
from app.core.database import get_db
from app.core.models.rules import Rule
from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum
from app.core.services.data_service import DataService
from app.core.services.util import create_new_rule, create_new_score_reason


# noinspection DuplicatedCode
def import_rule_identity_master(ds: DataService):
    # Delete all identities(I) rules
    # l2_rules: [Rule] = Rule.objects(Q(parent='I'))
    l2_rules: {Rule} = ds.get_rules({PARENT: IDENTITIES})
    for r in l2_rules:
        # l3_rules: [Rule] = Rule.objects(Q(parent=r.code))
        # l3_rules.delete()
        ds.delete_rules({PARENT: r[CODE]})
    # l2_rules.delete()
    ds.delete_rules({PARENT: IDENTITIES})

    # l1_rule = Rule.objects(Q(code='I'))
    # l1_rule.delete()
    ds.delete_rules({CODE: IDENTITIES})
    print('Identities(I) rules are deleted.')
    # define Identities(I)' rules master: level 1
    rule = create_new_rule(1, None, 'I', 'اطلاعات هویتی', 10, 100)
    ds.insert_rule(rule)
    print('Identities(I) master rule is created.')


def import_rules_identity_has_kycs_i1(ds: DataService):
    # define Identities(I)' rules of kycs master: level 2
    rule = create_new_rule(2, 'I', 'I1', 'احراز هویت', 4)
    ds.insert_rule(rule)

    # define Identities(I)' rules of kycs details: level 3
    # KYC = Yes	40	I0101P40    %4	احراز هویت نهایی از طریق استعلام ثبت احوال
    rule = create_new_rule(3, 'I1', 'I0101P40', 'احراز هویت نهایی از طریق استعلام ثبت احوال', 4, 40, 1)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # KYC = No	00	I0102P0 0%	عدم احراز هویت
    rule = create_new_rule(3, 'I1', 'I0102P0', 'عدم احراز هویت', 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Identities(I) has_kycs_i1 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: I1_RULES_PROFILE_HAS_KYCS})
    change_reason = create_new_score_reason(I1_RULES_PROFILE_HAS_KYCS, rule_codes, 'احراز هویت نهایی از طریق استعلام ثبت احوال')
    ds.insert_score_reason(change_reason)
    print('Identities(I) has_kycs_i1 change reasons are created.')


def import_rules_identity_military_service_status_i2(ds: DataService):
    # define Identities(I)' rules of military_service master: level 2
    rule = create_new_rule(2, 'I', 'I2', 'خدمت وظیفه عمومی', 2)
    ds.insert_rule(rule)

    # define Identities(I)' rules of military_service details: level 3
    # MilServiceFinished/Exempted/Ongoing	20  2%	I0201P20	پایان خدمت
    rule = create_new_rule(3, 'I2', 'I0201P20', 'پایان خدمت', 2, 20, ProfileMilitaryServiceStatusEnum.FINISHED.value)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # MilServiceFinished/Exempted/Ongoing	20  2%	I0202P20	 معافیت
    rule = create_new_rule(3, 'I2', 'I0202P20', 'معافیت', 2, 20, ProfileMilitaryServiceStatusEnum.EXEMPTED.value)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # MilServiceFinished/Exempted/Ongoing	20  2%	I0203P20	در حال خدمت
    rule = create_new_rule(3, 'I2', 'I0203P20', 'در حال خدمت', 2, 20, ProfileMilitaryServiceStatusEnum.ONGOING.value)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # MilServiceSubjected	00	I0204P0     0%	مشمول غیر غایب
    rule = create_new_rule(3, 'I2', 'I0204P0', 'مشمول غیر غایب', 2, 20, ProfileMilitaryServiceStatusEnum.SUBJECTED.value)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)

    # MilServiceAbsent	-50	I0205N50        -5% 	غایب
    rule = create_new_rule(3, 'I2', 'I0205N50', 'غایب', 5, -50, ProfileMilitaryServiceStatusEnum.ABSENT.value)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Identities(I) military_service_status_i2 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: I2_RULES_PROFILE_MILITARY_SERVICE_STATUS})
    change_reason = create_new_score_reason(I2_RULES_PROFILE_MILITARY_SERVICE_STATUS, rule_codes, 'بهبود وضعیت خدمت وظیفه عمومی', 'تنزل وضعیت خدمت وظیفه عمومی')
    ds.insert_score_reason(change_reason)
    print('Identities(I) military_service_status_i2 change reasons are created.')


def import_rules_identity_sim_card_ownerships_i3(ds: DataService):
    # define Identities(I)' rules of sim_care_ownership master: level 2
    rule = create_new_rule(2, 'I', 'I3', 'مالکیت خط تلفن همراه', 2)
    ds.insert_rule(rule)

    # define Identities(I)' rules of sim_care_ownership details: level 3
    # SimCardOwnership = Yes	20	I0301P20    2%	تطابق هویت واقعی کاربر با مشخصات مالک خط تلفن همراه در سامانه شاهکار
    rule = create_new_rule(3, 'I3', 'I0301P20', 'تطابق هویت واقعی کاربر با مشخصات مالک خط تلفن همراه در سامانه شاهکار', 2, 20, 1)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # SimCardOwnership = No	00	I0302P0     0%	عدم تطابق هویت واقعی کاربر با مشخصات مالک خط تلفن همراه
    rule = create_new_rule(3, 'I3', 'I0302P0', 'عدم تطابق هویت واقعی کاربر با مشخصات مالک خط تلفن همراه', 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Identities(I) sim_card_ownerships_i3 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: I3_RULES_PROFILE_SIM_CARD_OWNERSHIPS})
    change_reason = create_new_score_reason(I3_RULES_PROFILE_SIM_CARD_OWNERSHIPS, rule_codes, 'تایید مالکیت خط تلفن همراه', 'عدم تایید مالکیت خط تلفن همراه')
    ds.insert_score_reason(change_reason)
    print('Identities(I) sim_card_ownerships_i3 change reasons are created.')


def import_rules_identity_address_verifications_i4(ds: DataService):
    # define Identities(I)' rules of address_verifications master: level 2
    rule = create_new_rule(2, 'I', 'I4', 'احراز اصالت محل سکونت', 2)
    ds.insert_rule(rule)

    # define Identities(I)' rules of address_verifications details: level 3
    # AddressVerification = Yes	20	I0401P20    2%	احراز اصالت نشانی محل سکونت کاربر از طریق وارد کردن رمز پستی
    rule = create_new_rule(3, 'I4', 'I0401P20', 'احراز اصالت نشانی محل سکونت کاربر از طریق وارد کردن رمز پستی', 2, 20, 1)
    ds.insert_rule(rule)
    rule_codes: List[str] = [rule.code]

    # AddressVerification = No	00	I0402P0 0%	عدم احراز اصالت نشانی محل سکونت کاربر
    rule = create_new_rule(3, 'I4', 'I0402P0', 'تطابق هویت واقعی کاربر با مشخصات مالک خط تلفن همراه در سامانه شاهکار', 0, 0, 0)
    ds.insert_rule(rule)
    rule_codes.append(rule.code)
    print('Identities(I) address_verifications_i4 rules are created.')
    ds.delete_score_reasons({RULE_MASTER_CODE: I4_RULES_PROFILE_ADDRESS_VERIFICATIONS})
    change_reason = create_new_score_reason(I4_RULES_PROFILE_ADDRESS_VERIFICATIONS, rule_codes, 'تایید نشانی محل سکونت', 'عدم تایید نشانی محل سکونت')
    ds.insert_score_reason(change_reason)
    print('Identities(I) address_verifications_i4 change reasons are created.')


def import_rules_identities(ds: DataService):
    import_rule_identity_master(ds)
    import_rules_identity_has_kycs_i1(ds)
    import_rules_identity_military_service_status_i2(ds)
    import_rules_identity_sim_card_ownerships_i3(ds)
    import_rules_identity_address_verifications_i4(ds)


if __name__ == '__main__':
    import_rules_identities(DataService(get_db()))
