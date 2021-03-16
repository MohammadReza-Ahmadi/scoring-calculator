import random
from datetime import date

from app.core.database import get_db
from app.core.models.profile import Profile
from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum
from app.core.services.data_service import DataService

if __name__ == '__main__':
    ds = DataService(get_db())
    ds.delete_profiles({})
    for i in range(2):
        p = Profile(user_id=int(100 + i))
        p.has_kyc = 1
        p.military_service_status = ProfileMilitaryServiceStatusEnum.FINISHED
        p.sim_card_ownership = 1
        p.address_verification = 1
        p.membership_date = date.today()
        p.recommended_to_others_count = 23
        p.star_count_average = 1

        p.identities_score = random.randint(0, 100)  # 10%
        p.histories_score = random.randint(0, 300)  # 30%
        p.volumes_score = random.randint(0, 250)  # 25%
        p.timeliness_score = random.randint(0, 350)  # 35%
        p.score = p.identities_score + p.histories_score + p.volumes_score + p.timeliness_score
        ds.insert_profile(p)

        # Test aggregation pipeline run performance
        # pipeline = generate_scores_distributions_pipeline(0, 1000, 20)
        # ref: CommandCursor = ds.db.profiles.aggregate(pipeline)
        # ref: CommandCursor = ds.db.profiles.aggregate(scores_distributions_pipeline)

        # print(ref[0].get('0_to_50'))
        # for r in ref:
        #     print(r)
