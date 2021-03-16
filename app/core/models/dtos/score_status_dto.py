from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.core.models.score_gauges import ScoreGauge


class ScoreStatusDTO(BaseModel):
    score: int = 0
    max_score: int = 0
    score_gauges: List[ScoreGauge] = []
    last_score_change: int = 0
    last_update_date: datetime = 0
