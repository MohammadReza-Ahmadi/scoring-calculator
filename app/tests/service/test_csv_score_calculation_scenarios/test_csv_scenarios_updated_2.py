import csv
from datetime import date, timedelta

from app.core.constants import ALL_USERS_AVERAGE_UNFIXED_RETURNED_CHEQUES_AMOUNT, IDENTITIES_SCORE, HISTORIES_SCORE, \
    VOLUMES_SCORE, \
    TIMELINESS_SCORE, ALL_USERS_AVERAGE_PRINCIPAL_INTEREST_AMOUNT, ALL_USERS_AVERAGE_DEAL_AMOUNT, USER_ID
from app.core.data.caching.redis_caching import RedisCaching
from app.core.models.cheques import Cheque
from app.core.models.done_trades import DoneTrade
from app.core.models.loans import Loan
from app.core.models.profile import Profile
from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum
from app.core.models.undone_trades import UndoneTrade
from app.core.services.data_service import DataService
from app.core.services.score_calculation_service_2 import ScoreCalculationService_2


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


def calculate_score(scenarios_dicts: [], user_id: int):
    # mongoengine_api.launch_app()
    ds = DataService()
    rds = RedisCaching(ds)
    cs = ScoreCalculationService_2(rds, ds)
    # crm = RedisCachingRulesMasters(rds.rds)

    for scn_dict in scenarios_dicts:
        expected_score = scn_dict['Vscore']

        # DoneTrade Score Calculation ..................................................
        dt = ds.get_user_done_trade(user_id)
        if dt is None:
            dt = DoneTrade(user_id=user_id)
            dt.timely_trades_count_of_last_3_months = scn_dict['Last3MSD']
            dt.timely_trades_count_between_last_3_to_12_months = scn_dict['Last1YSD']
            dt.past_due_trades_count_of_last_3_months = scn_dict['B30DayDelayLast3M']
            dt.past_due_trades_count_between_last_3_to_12_months = scn_dict['B30DayDelayLast3-12M']
            dt.arrear_trades_count_of_last_3_months = scn_dict['A30DayDelayLast3M']
            dt.arrear_trades_count_between_last_3_to_12_months = scn_dict['A30DayDelay3-12M']
            dt.total_delay_days = scn_dict['AverageDelayRatio']
            # todo: 100000000 is fix Denominator that is all_other_users_done_trades_amount, it should be change later
            dt.trades_total_balance = round(float(scn_dict['SDealAmountRatio']) * ALL_USERS_AVERAGE_DEAL_AMOUNT)
            ds.insert_done_trade(dt)

        done_trades_score = cs.calculate_user_done_trades_score_2(user_id=0, modified_done_trade=dt)


        # UndoneTrade Score Calculation ..................................................
        udt = UndoneTrade(user_id=user_id)
        udt.undue_trades_count = scn_dict['NumNotDueDeal']
        udt.past_due_trades_count = scn_dict['UnfinishedB30DayDelay']
        udt.arrear_trades_count = scn_dict['UnfinishedA30DayDelay']
        udt.undue_trades_total_balance_of_last_year = round(
            float(scn_dict['NotDueDealAmountRatio']) * dt.trades_total_balance)
        udt.past_due_trades_total_balance_of_last_year = round(
            float(scn_dict['UnfinishedB30Din1YRatio']) * dt.trades_total_balance)
        udt.arrear_trades_total_balance_of_last_year = round(
            float(scn_dict['UnfinishedA30Din1YRatio']) * dt.trades_total_balance)
        undone_trades_score = cs.calculate_user_undone_trades_score_2(user_id=0, undone_trade_object=udt,
                                                                      done_trade_object=dt)
        ds.delete_undone_trades({USER_ID: user_id})
        ds.insert_undone_trade(udt)

        # Loan Score Calculation ..................................................
        ln = Loan(user_id=user_id)
        ln.loans_total_count = scn_dict['Loans']
        ln.loans_total_balance = ALL_USERS_AVERAGE_PRINCIPAL_INTEREST_AMOUNT
        ln.past_due_loans_total_count = int(scn_dict['PastDueLoans'])
        ln.arrear_loans_total_count = int(scn_dict['DelayedLoans'])
        ln.suspicious_loans_total_count = int(scn_dict['DoubfulCollectionLoans'])
        ln.monthly_installments_total_balance = float(scn_dict['MonthlyInstallments'])
        ln.overdue_loans_total_balance = round(float(scn_dict['CurrentLoanAmountRatio']) * ln.loans_total_balance)
        ln.past_due_loans_total_balance = round(float(scn_dict['PastDueLoanAmountRatio']) * ln.loans_total_balance)
        ln.arrear_loans_total_balance = round(float(scn_dict['DelayedLoanAmountRatio']) * ln.loans_total_balance)
        ln.suspicious_loans_total_balance = round(
            float(scn_dict['DoubtfulCollectionAmountRatio']) * ln.loans_total_balance)
        loan_score = cs.calculate_user_loans_score_2(user_id=0, loan_object=ln)
        ds.delete_loans({USER_ID: user_id})
        ds.insert_loan(ln)

        # Cheque Score Calculation ..................................................
        ch = Cheque(user_id=user_id)
        ch.unfixed_returned_cheques_count_of_last_3_months = scn_dict['DishonouredChequesL3M']
        ch.unfixed_returned_cheques_count_between_last_3_to_12_months = scn_dict['DishonouredChequesL3-12M']
        ch.unfixed_returned_cheques_count_of_more_12_months = scn_dict['DishonouredChequesA12M']
        ch.unfixed_returned_cheques_count_of_last_5_years = scn_dict['AllDishonouredCheques']
        ch.unfixed_returned_cheques_total_balance = round(
            float(scn_dict['DCAmountRatio']) * ALL_USERS_AVERAGE_UNFIXED_RETURNED_CHEQUES_AMOUNT)
        cheque_score: [] = cs.calculate_user_cheques_score_2(user_id=0, cheque_object=ch)
        ds.delete_cheques({USER_ID: user_id})
        ds.insert_cheque(ch)

        # Profile Score Calculation ..................................................

        if user_id is not None:
            ds.delete_profiles({USER_ID: user_id})
        p = Profile(user_id=user_id)
        p.has_kyc = scn_dict['KYC']
        p.military_service_status = ProfileMilitaryServiceStatusEnum.__getitem__(scn_dict['Military'])
        p.sim_card_ownership = scn_dict['SimCard']
        p.address_verification = scn_dict['Address']
        p.membership_date = date.today() - timedelta(days=int(scn_dict['Membership']))
        p.recommended_to_others_count = scn_dict['Recommendation']
        p.star_count_average = scn_dict['WeightedAveStars']
        profile_score = cs.calculate_user_profile_score_2(user_id=0, profile_object=p)

        # total_pure_score = int(profile_score) + int(done_trades_score) + int(undone_trades_score) + int(loan_score) + int(cheque_score)

        identities_pure_score = cs.scores_dict.get(IDENTITIES_SCORE)
        identities_normalized_score = cs.calculate_identities_normalized_score_2(identities_pure_score)

        histories_pure_score = cs.scores_dict.get(HISTORIES_SCORE)
        histories_normalized_score = cs.calculate_histories_normalized_score_2(histories_pure_score)

        volumes_pure_score = cs.scores_dict.get(VOLUMES_SCORE)
        volumes_normalized_score = cs.calculate_volumes_normalized_score_2(volumes_pure_score)

        timeliness_pure_score = cs.scores_dict.get(TIMELINESS_SCORE)
        timeliness_normalized_score = cs.calculate_timeliness_normalized_score_2(timeliness_pure_score)

        total_pure_score = identities_pure_score + histories_pure_score + volumes_pure_score + timeliness_pure_score
        total_normalized_score = identities_normalized_score + histories_normalized_score + volumes_normalized_score + timeliness_normalized_score
        print('<><><><><><><> expected-score= {} , total_pure_score = {} and total_normalized_score = {} '
              '<><><><><><><>'.format(expected_score, total_pure_score, total_normalized_score))

        # Profile Score insertion
        p.score = total_normalized_score
        p.identities_score = identities_normalized_score
        p.histories_score = histories_normalized_score
        p.volumes_score = volumes_normalized_score
        p.timeliness_score = timeliness_normalized_score
        ds.delete_profiles({USER_ID: user_id})
        ds.insert_profile(p)

        # final_score = int(profile_score[0]) + int(done_trades_score[0]) + int(undone_trades_score[0]) + int(loan_score[0]) + int(cheque_score[0])
        # normalized_final_score = profile_score[1] + done_trades_score[1] + undone_trades_score[1] + loan_score[1] + cheque_score[1]

        # print('<><><><><><><> expected-score= {} , final-score = {} and normalized_final_score = {}
        # <><><><><><><>'.format(expected_score, final_score,normalized_final_score))


if __name__ == '__main__':
    # csv_file_path = '/home/vsq-docs-live/scoring/_@RISK-Files/Vscore-sample-scenario.csv'
    # csv_file_path = '/home/vsq-docs-live/scoring/_@RISK-Files/new-scenarios/Vscore-scenario-1.csv'
    # csv_file_path = '/home/vsq-docs-live/scoring/_@RISK-Files/Vscore-scenario-dr.csv'
    # csv_file_path = '/home/vsq-docs-live/scoring/_@RISK-Files/Vscore-scenario-gh.csv'
    csv_file_path = '/home/mohammad-reza/Documents/vsq-docs-live/scoring/_@RISK-Files/Vscore-scenario-soleimanikhah.csv'

    # NEW SCENARIOS ########################
    csv_file_path = '/home/mohammad-reza/Documents/vsq-docs-live/scoring/SCENARIOS/2-vscore-scenario.csv'
    sen_dict = read_scenarios_dicts_from_csv(csv_file_path)
    user_id = 2
    calculate_score(sen_dict, user_id)
