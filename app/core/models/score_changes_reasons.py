from typing import List

from pydantic import BaseModel


class ScoreChangeReason(BaseModel):
    rule_master_code: str = None
    rule_codes: List[str] = None
    positive_reason: str = None
    negative_reason: str = None
