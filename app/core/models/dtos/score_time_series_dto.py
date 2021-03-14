from datetime import date

from pydantic import BaseModel


class ScoreTimeSeriesDTO(BaseModel):
    score_date: date = None
    score: int = None
