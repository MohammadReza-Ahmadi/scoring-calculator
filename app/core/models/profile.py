from datetime import date, datetime

from pydantic import BaseModel

from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum


class Profile(BaseModel):
    user_id: int = None

    has_kyc: bool = False
    has_kyc_score: int = None

    military_service_status: ProfileMilitaryServiceStatusEnum = ProfileMilitaryServiceStatusEnum.FINISHED
    military_service_status_score: int = None

    sim_card_ownership: bool = False
    sim_card_ownership_score: int = None

    address_verification: bool = False
    address_verification_score: int = None

    membership_date: date = None
    membership_date_score: int = None

    recommended_to_others_count: int = None
    recommended_to_others_count_score: int = None

    number_of_times_star_received: int = None
    number_of_times_star_received_score: int = None

    star_count_average: int = None
    star_count_average_score: int = None

    score: int = None
    identities_score: int = None
    histories_score: int = None
    volumes_score: int = None
    timeliness_score: int = None

    # class Config:
    #     orm_mode = True

    # Profile = create_model(
    #     'BarModel',
    #     apple='russet',
    #     banana='yellow',
    #     __base__=FooModel,
    # )

