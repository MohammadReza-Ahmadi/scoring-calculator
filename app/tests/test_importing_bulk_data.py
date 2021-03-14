import unittest
from datetime import datetime, date

import dateutil
import jdatetime

from app.core import mongoengine_api
from app.core.database import get_db
from app.core.models.done_trades import DoneTrade
from app.core.models.score_time_series import ScoreTimeSeries
from app.core.services import general_data_service as gs
from app.core.services.util import get_random_digits_str


class TestImportRandomBulkData(unittest.TestCase):
    def setUp(self):
        mongoengine_api.launch_app()
        #     lower = get_random_lowercase_str(3)
        #     print(lower)
        #     upper = get_random_uppercase_str(7)
        #     print(upper)
        #     letters = get_random_letters_str(9)
        #     print(letters)
        #     digits = get_random_digits_str(24)
        #     print(digits)
        #     punctuation = get_random_punctuation_str(11)
        #     print(punctuation)

    def test_get_bulk_data(self):
        done_trades: DoneTrade = DoneTrade.objects(user_id=1).all()
        # print(user.to_json())
        print("all doneTrades are loaded.")
        for dt in done_trades:
            print(dt.to_json())

    def test_import_done_trades_data(self):
        DoneTrade.drop_collection()
        for i in range(1):
            dt = DoneTrade()
            dt.user_id = 1
            dt.timely_trades_count_of_last_3_months = get_random_digits_str(2)
            dt.timely_trades_count_between_last_3_to_12_months = get_random_digits_str(2)
            dt.past_due_trades_count_of_last_3_months = get_random_digits_str(2)
            dt.past_due_trades_count_between_last_3_to_12_months = get_random_digits_str(2)
            dt.arrear_trades_count_of_last_3_months = get_random_digits_str(2)
            dt.arrear_trades_count_between_last_3_to_12_months = get_random_digits_str(2)
            dt.trades_total_balance = get_random_digits_str(9)
            dt.total_delay_days = get_random_digits_str(2)
            gs.save_document(dt)
            print("flowing document is saved: ", dt.to_json())

    def test_import_score_time_series_bulk_data(self):
        db = get_db()
        db.scoreTimeSeries.delete_many({})
        score = 330
        for i in range(365):
            d = jdatetime.timedelta(days=365-i)
            score_date = datetime.today().__sub__(d)
            # score_date = dateutil.parser.parse(score_date.isoformat())
            if i <= 30:
                score += 1
            elif i <= 50:
                score -= 1
            elif i <= 80:
                score += 1
            elif i <= 99:
                score = score
            elif i <= 115:
                score = score
            elif i <= 140:
                score += 1
            elif i <= 160:
                score -= 1
            elif i <= 190:
                score = score
            elif i <= 260:
                score += 1
            elif i <= 285:
                score = score
            elif i <= 325:
                score -= 1
            elif i <= 365:
                score += 1
            db.scoreTimeSeries.insert_one(dict(ScoreTimeSeries(user_id=1, score_date=score_date, score=score)))
            print('ScoreTimeSeries(user_id:{}, score_date:{}, score:{}) is inserted.'.format(1, score_date, score))

