from datetime import date

from pydantic import BaseModel


class Cheque(BaseModel):
    user_id: int = None

    # count fields
    unfixed_returned_cheques_count_of_last_3_months: int = None
    unfixed_returned_cheques_count_of_last_3_months_score: int = None

    unfixed_returned_cheques_count_between_last_3_to_12_months: int = None
    unfixed_returned_cheques_count_between_last_3_to_12_months_score: int = None

    unfixed_returned_cheques_count_of_more_12_months: int = None
    unfixed_returned_cheques_count_of_more_12_months_score: int = None

    unfixed_returned_cheques_count_of_last_5_years: int = None
    unfixed_returned_cheques_count_of_last_5_years_score: int = None

    # balance fields
    unfixed_returned_cheques_total_balance: float = None
    unfixed_returned_cheques_total_balance_score: int = None
