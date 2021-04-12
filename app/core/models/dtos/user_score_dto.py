from datetime import date

from pydantic import BaseModel


class UserScoreDTO(BaseModel):
    user_id: int = None
    score: int = None
