import csv
from datetime import date, timedelta

from app.core.data.caching.redis_caching import RedisCaching
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
        rev_pf = Profile(user_id=user_id)
        rev_pf.has_kyc = scn_dict['KYC']
        rev_pf.military_service_status = ProfileMilitaryServiceStatusEnum.__getitem__(scn_dict['Military'])
        rev_pf.sim_card_ownership = scn_dict['SimCard']
        rev_pf.address_verification = scn_dict['Address']
        rev_pf.membership_date = date.today() - timedelta(days=int(scn_dict['Membership']))
        rev_pf.recommended_to_others_count = scn_dict['Recommendation']
        rev_pf.star_count_average = scn_dict['WeightedAveStars']
        rec_pf = ds.get_user_profile(user_id)
        profile_score = cs.calculate_user_profile_score(user_id=user_id, recent_pf=rec_pf, revised_pf=rev_pf)


if __name__ == '__main__':
    csv_file_path = '/home/mohammad-reza/Documents/vsq-docs-live/scoring/SCENARIOS/2-vscore-scenario.csv'
    sen_dict = read_scenarios_dicts_from_csv(csv_file_path)
    user_id = 100
    calculate_score(sen_dict, user_id)
