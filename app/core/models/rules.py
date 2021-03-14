from pydantic import BaseModel, Field


class Rule(BaseModel):
    level: int = Field(None)
    code: str = Field(None)
    parent: str = Field(None)
    title: str = Field(None)
    impact_percent: float = Field(None)
    score: int = Field(None)
    min: float = Field(None)
    max: float = Field(None)
    pos_change_reason: str = Field(None)  # positive change reason
    neg_change_reason: str = Field(None)  # negative change reason

    # parameterized constructor
    # def __init__(self, level, code: str, title: str, impact_percent: float, score: int = None, min_val: float = None, max_val: float = None):
    #     self.level = level
    #     self.code = code
    #     self.title = title
    #     self.impact_percent = impact_percent
    #     self.score = score
    #     self.min = min_val
    #     self.max = min_val if max_val is None else max_val

    # meta = {
    #     'db_alias': 'core',
    #     'collection': 'rules'
    # }
