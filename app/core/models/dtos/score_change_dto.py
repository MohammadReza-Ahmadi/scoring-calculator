from datetime import date

from pydantic import BaseModel


class ScoreChangeDTO(BaseModel):
    change_reason: str = None
    change_date: date = None
    score_change: int = None
