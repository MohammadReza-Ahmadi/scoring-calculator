import csv
from datetime import date, timedelta

from app.core.constants import ALL_USERS_AVERAGE_DEAL_AMOUNT, ALL_USERS_AVERAGE_PRINCIPAL_INTEREST_AMOUNT, ALL_USERS_AVERAGE_UNFIXED_RETURNED_CHEQUES_AMOUNT
from app.core.data.caching.redis_caching import RedisCaching
from app.core.models.cheques import Cheque
from app.core.models.done_trades import DoneTrade
from app.core.models.loans import Loan
from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum
from app.core.models.undone_trades import UndoneTrade
from app.core.services.data_service import DataService
from app.core.services.score_calculation_service import ScoreCalculationService
from app.core.services.util import is_not_none, get_zero_if_none, create_revised_profile


def read_scenarios_dicts_from_csv(csv_path):
    scenarios_dicts = []
    with open(csv_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            # col_values = ', '.join(row).split(',')
            if line_count == 0:
                print(f'Column names are:\n {", ".join(row)}')
            line_count += 1
            scenarios_dicts.append(row)
        print(f'Processed {line_count} lines.')
    return scenarios_dicts


# noinspection DuplicatedCode
def calculate_score(scenarios_dicts: [], user_id: int):
    ds = DataService()
    rds = RedisCaching(ds)
    cs = ScoreCalculationService(rds, ds)

    for scn_dict in scenarios_dicts:
        # Profile Score Calculation ..................................................
        recent_p = ds.get_user_profile(user_id)
        revised_p = create_revised_profile(user_id=user_id, recent_p=recent_p)
        if is_not_none(scn_dict['KYC']):
            revised_p.has_kyc = scn_dict['KYC']
        if is_not_none(scn_dict['Military']):
            revised_p.military_service_status = ProfileMilitaryServiceStatusEnum.__getitem__(scn_dict['Military'])
        if is_not_none(scn_dict['SimCard']):
            revised_p.sim_card_ownership = scn_dict['SimCard']
        if is_not_none(scn_dict['Address']):
            revised_p.address_verification = scn_dict['Address']
        if is_not_none(scn_dict['Membership']):
            revised_p.membership_date = date.today() - timedelta(days=int(scn_dict['Membership']))
        if is_not_none(scn_dict['Recommendation']):
            revised_p.recommended_to_others_count = scn_dict['Recommendation']
        if is_not_none(scn_dict['WeightedAveStars']):
            revised_p.star_count_average = scn_dict['WeightedAveStars']
        cs.calculate_user_profile_score(recent_p=recent_p, revised_p=revised_p)

        # DoneTrade Score Calculation ..................................................
        dt = DoneTrade(user_id=user_id)
        if is_not_none(scn_dict['Last3MSD']):
            dt.timely_trades_count_of_last_3_months = scn_dict['Last3MSD']
        if is_not_none(scn_dict['Last1YSD']):
            dt.timely_trades_count_between_last_3_to_12_months = scn_dict['Last1YSD']
        if is_not_none(scn_dict['B30DayDelayLast3M']):
            dt.past_due_trades_count_of_last_3_months = scn_dict['B30DayDelayLast3M']
        if is_not_none(scn_dict['B30DayDelayLast3-12M']):
            dt.past_due_trades_count_between_last_3_to_12_months = scn_dict['B30DayDelayLast3-12M']
        if is_not_none(scn_dict['A30DayDelayLast3M']):
            dt.arrear_trades_count_of_last_3_months = scn_dict['A30DayDelayLast3M']
        if is_not_none(scn_dict['A30DayDelay3-12M']):
            dt.arrear_trades_count_between_last_3_to_12_months = scn_dict['A30DayDelay3-12M']
        if is_not_none(scn_dict['AverageDelayRatio']):
            dt.total_delay_days = scn_dict['AverageDelayRatio']
        if is_not_none(scn_dict['SDealAmountRatio']):
            # todo: 100000000 is fix Denominator that is all_other_users_done_trades_amount, it should be change later
            dt.trades_total_balance = round(float(scn_dict['SDealAmountRatio']) * ALL_USERS_AVERAGE_DEAL_AMOUNT)
        recent_dt = ds.get_user_done_trade(user_id)
        cs.calculate_user_done_trades_score(revised_p=revised_p, recent_dt=recent_dt, revised_dt=dt)
        ds.insert_or_update_done_trade(dt, update_flag=recent_dt.user_id is not None)

        # UndoneTrade Score Calculation ..................................................
        udt = UndoneTrade(user_id=user_id)
        if is_not_none(scn_dict['NumNotDueDeal']):
            udt.undue_trades_count = scn_dict['NumNotDueDeal']
        if is_not_none(scn_dict['UnfinishedB30DayDelay']):
            udt.past_due_trades_count = scn_dict['UnfinishedB30DayDelay']
        if is_not_none(scn_dict['UnfinishedA30DayDelay']):
            udt.arrear_trades_count = scn_dict['UnfinishedA30DayDelay']
        dt.trades_total_balance = get_zero_if_none(dt.trades_total_balance)
        if is_not_none(scn_dict['NotDueDealAmountRatio']):
            udt.undue_trades_total_balance_of_last_year = round(float(scn_dict['NotDueDealAmountRatio']) * dt.trades_total_balance)
        if is_not_none(scn_dict['UnfinishedB30Din1YRatio']):
            udt.past_due_trades_total_balance_of_last_year = round(float(scn_dict['UnfinishedB30Din1YRatio']) * dt.trades_total_balance)
        if is_not_none(scn_dict['UnfinishedA30Din1YRatio']):
            udt.arrear_trades_total_balance_of_last_year = round(float(scn_dict['UnfinishedA30Din1YRatio']) * dt.trades_total_balance)
        recent_udt = ds.get_user_undone_trade(user_id)
        cs.calculate_user_undone_trades_score(revised_p=revised_p, recent_udt=recent_udt, revised_udt=udt, dt=dt)
        ds.insert_or_update_undone_trade(udt, update_flag=recent_udt.user_id is not None)

        # Loan Score Calculation ..................................................
        ln = Loan(user_id=user_id)
        if is_not_none(scn_dict['Loans']):
            ln.loans_total_count = scn_dict['Loans']
        ln.loans_total_balance = ALL_USERS_AVERAGE_PRINCIPAL_INTEREST_AMOUNT
        if is_not_none(scn_dict['PastDueLoans']):
            ln.past_due_loans_total_count = int(scn_dict['PastDueLoans'])
        if is_not_none(scn_dict['DelayedLoans']):
            ln.arrear_loans_total_count = int(scn_dict['DelayedLoans'])
        if is_not_none(scn_dict['DoubfulCollectionLoans']):
            ln.suspicious_loans_total_count = int(scn_dict['DoubfulCollectionLoans'])
        if is_not_none(scn_dict['MonthlyInstallments']):
            ln.monthly_installments_total_balance = float(scn_dict['MonthlyInstallments'])
        if is_not_none(scn_dict['CurrentLoanAmountRatio']):
            ln.overdue_loans_total_balance = round(float(scn_dict['CurrentLoanAmountRatio']) * ln.loans_total_balance)
        if is_not_none(scn_dict['PastDueLoanAmountRatio']):
            ln.past_due_loans_total_balance = round(float(scn_dict['PastDueLoanAmountRatio']) * ln.loans_total_balance)
        if is_not_none(scn_dict['DelayedLoanAmountRatio']):
            ln.arrear_loans_total_balance = round(float(scn_dict['DelayedLoanAmountRatio']) * ln.loans_total_balance)
        if is_not_none(scn_dict['DoubtfulCollectionAmountRatio']):
            ln.suspicious_loans_total_balance = round(float(scn_dict['DoubtfulCollectionAmountRatio']) * ln.loans_total_balance)
        recent_ln = ds.get_user_loan(user_id)
        loan_score = cs.calculate_user_loans_score(revised_p=revised_p, recent_ln=recent_ln, revised_ln=ln)
        ds.insert_or_update_loan(ln, update_flag=recent_ln.user_id is not None)

        # Cheque Score Calculation ..................................................
        ch = Cheque(user_id=user_id)
        if is_not_none(scn_dict['DishonouredChequesL3M']):
            ch.unfixed_returned_cheques_count_of_last_3_months = scn_dict['DishonouredChequesL3M']
        if is_not_none(scn_dict['DishonouredChequesL3-12M']):
            ch.unfixed_returned_cheques_count_between_last_3_to_12_months = scn_dict['DishonouredChequesL3-12M']
        if is_not_none(scn_dict['DishonouredChequesA12M']):
            ch.unfixed_returned_cheques_count_of_more_12_months = scn_dict['DishonouredChequesA12M']
        if is_not_none(scn_dict['AllDishonouredCheques']):
            ch.unfixed_returned_cheques_count_of_last_5_years = scn_dict['AllDishonouredCheques']
        if is_not_none(scn_dict['DCAmountRatio']):
            ch.unfixed_returned_cheques_total_balance = round(float(scn_dict['DCAmountRatio']) * ALL_USERS_AVERAGE_UNFIXED_RETURNED_CHEQUES_AMOUNT)
        recent_ch = ds.get_user_cheque(user_id)
        cheque_score = cs.calculate_user_cheques_score(revised_p=revised_p, recent_ch=recent_ch, revised_ch=ch)
        ds.insert_or_update_cheque(ch, update_flag=recent_ch.user_id is not None)
        ds.insert_or_update_profile(revised_p, update_flag=recent_p.user_id is not None)


if __name__ == '__main__':
    csv_file_path = '/home/mohammad-reza/Documents/vsq-docs-live/scoring/SCENARIOS/3-vscore-scenario.csv'
    sen_dict = read_scenarios_dicts_from_csv(csv_file_path)
    user_id = 2
    calculate_score(sen_dict, user_id)
