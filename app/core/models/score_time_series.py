from datetime import datetime
from pydantic import BaseModel


class ScoreTimeSeries(BaseModel):
    user_id: int = None
    score_date: datetime = None
    score: int = None
