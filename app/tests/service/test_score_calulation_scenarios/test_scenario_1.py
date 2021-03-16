import unittest
from _datetime import datetime
from datetime import timedelta

from app.core import mongoengine_api
from app.core.models.cheques import Cheque
from app.core.models.done_trades import DoneTrade
from app.core.models.loans import Loan
from app.core.models.profile import Profile
from app.core.models.undone_trades import UndoneTrade
from app.core.models.scoring_enums import ProfileMilitaryServiceStatusEnum
from app.core.services.score_calculation_service import ScoreCalculationService
from app.core.services import general_data_service as gs


class TestScenario1(unittest.TestCase):
    uid = 2

    def import_profile_data(self):
        Profile.objects(user_id=self.uid).delete()
        p = Profile()
        p.user_id = self.uid
        p.has_kyc = True
        p.military_service_status = ProfileMilitaryServiceStatusEnum.SUBJECTED
        p.sim_card_ownership = False
        p.address_verification = False
        p.membership_date = datetime.now() - timedelta(2)
        p.recommended_to_others_count = 0
        p.star_count_average = 4
        p.score = 0
        gs.save_document(p)

    def import_done_trades_data(self):
        DoneTrade.objects(user_id=self.uid).delete()
        dt = DoneTrade()
        dt.drop_collection()

        dt.user_id = self.uid
        dt.calculation_start_date = datetime.now()
        dt.timely_trades_count_of_last_3_months = 1
        dt.timely_trades_count_between_last_3_to_12_months = 0
        dt.past_due_trades_count_of_last_3_months = 0
        dt.past_due_trades_count_between_last_3_to_12_months = 0
        dt.arrear_trades_count_of_last_3_months = 0
        dt.arrear_trades_count_between_last_3_to_12_months = 0
        dt.trades_total_balance = 45000000
        dt.total_delay_days = 0
        dt.save()

    def import_undone_trades_data(self):
        UndoneTrade.objects(user_id=self.uid).delete()
        dt = UndoneTrade()
        dt.drop_collection()

        dt.user_id = self.uid
        dt.calculation_start_date = datetime.now()
        dt.calculation_start_date = datetime.now()
        dt.undue_trades_count = 0
        dt.past_due_trades_count = 0
        dt.arrear_trades_count = 0
        dt.undue_trades_total_balance_of_last_year = 45000000
        dt.past_due_trades_total_balance_of_last_year = 0
        dt.arrear_trades_total_balance_of_last_year = 0
        dt.save()

    def import_cheque_data(self):
        Cheque.objects(user_id=self.uid).delete()
        ch = Cheque()
        ch.drop_collection()
        ch.user_id = self.uid
        ch.unfixed_returned_cheques_count_of_last_3_months = 0
        ch.unfixed_returned_cheques_count_between_last_3_to_12_months = 0
        ch.unfixed_returned_cheques_count_of_more_12_months = 0
        ch.unfixed_returned_cheques_count_of_last_5_years = 0
        ch.unfixed_returned_cheques_total_balance = 0
        ch.save()

    def import_loan_data(self):
        Loan.objects(user_id=self.uid).delete()
        ln = Loan()
        ln.drop_collection()
        ln.user_id = self.uid
        ln.loans_total_count = 0
        ln.loans_total_balance = 0
        ln.past_due_loans_total_count = 0
        ln.arrear_loans_total_count = 0
        ln.suspicious_loans_total_count = 0
        ln.monthly_installments_total_balance = 0
        ln.overdue_loans_total_balance = 0
        ln.past_due_loans_total_balance = 0
        ln.arrear_loans_total_balance = 0
        ln.suspicious_loans_total_balance = 0
        ln.save()

    def test_calculate_final_score(self):
        mongoengine_api.launch_app()
        rds = RedisCaching()
        cs = ScoreCalculationService(rds)
        cs.calculate_user_final_score(self.uid)


if __name__ == '__main__':
    mongoengine_api.launch_app()
    t = TestScenario1()
    t.import_profile_data()
    # t.import_done_trades_data()
    # t.import_undone_trades_data()
    # t.import_cheque_data()
    # t.import_loan_data()
    # t.test_calculate_final_score()
