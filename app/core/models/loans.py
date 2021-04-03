from pydantic.main import BaseModel


class Loan(BaseModel):
    user_id: int = None

    # count fields
    loans_total_count: int = None
    loans_total_count_score: int = None

    loans_total_balance: float = None
    loans_total_balance_score: int = None

    past_due_loans_total_count: int = None
    past_due_loans_total_count_score: int = None

    arrear_loans_total_count: int = None
    arrear_loans_total_count_score: int = None

    suspicious_loans_total_count: int = None
    suspicious_loans_total_count_score: int = None

    # balance fields
    monthly_installments_total_balance: float = None
    monthly_installments_total_balance_score: int = None

    overdue_loans_total_balance: float = None
    overdue_loans_total_balance_score: int = None

    past_due_loans_total_balance: float = None
    past_due_loans_total_balance_score: int = None

    arrear_loans_total_balance: float = None
    arrear_loans_total_balance_score: int = None

    suspicious_loans_total_balance: float = None
    suspicious_loans_total_balance_score: int = None
