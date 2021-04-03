import csv
from datetime import date, timedelta, datetime

from app.core.constants import ALL_USERS_AVERAGE_DEAL_AMOUNT
from app.core.data.caching.redis_caching import RedisCaching
from app.core.models.done_trades import DoneTrade
from app.core.models.profile import Profile
from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum
from app.core.services.data_service import DataService
from app.core.services.score_calculation_service import ScoreCalculationService


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
        p = Profile(user_id=user_id)
        p.has_kyc = scn_dict['KYC']
        p.military_service_status = ProfileMilitaryServiceStatusEnum.__getitem__(scn_dict['Military'])
        p.sim_card_ownership = scn_dict['SimCard']
        p.address_verification = scn_dict['Address']
        p.membership_date = date.today() - timedelta(days=int(scn_dict['Membership']))
        p.recommended_to_others_count = scn_dict['Recommendation']
        p.star_count_average = scn_dict['WeightedAveStars']
        recent_p = ds.get_user_profile(user_id)
        profile_score = cs.calculate_user_profile_score(p=p, recent_p=recent_p)
        ds.insert_or_update_profile(p, update_flag=recent_p.user_id is not None)

        # DoneTrade Score Calculation ..................................................
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
        recent_dt = ds.get_user_done_trade(user_id)
        done_trades_score = cs.calculate_user_done_trades_score(p=p, recent_dt=recent_dt, revised_dt=dt)
        ds.insert_or_update_done_trade(dt, update_flag=recent_dt.user_id is not None)


if __name__ == '__main__':
    csv_file_path = '/home/mohammad-reza/Documents/vsq-docs-live/scoring/SCENARIOS/2-vscore-scenario.csv'
    sen_dict = read_scenarios_dicts_from_csv(csv_file_path)
    user_id = 3
    calculate_score(sen_dict, user_id)
