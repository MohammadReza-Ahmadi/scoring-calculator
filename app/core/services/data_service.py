from datetime import datetime, date, timedelta
from typing import List

import dateutil
from pydantic import parse_obj_as
from pymongo.command_cursor import CommandCursor
from pymongo.cursor import Cursor
from pymongo.database import Database

from app.core.constants import USER_ID, DAYS, MONTHS, SCORE_DISTRIBUTION_SEPARATOR, ZERO, ONE, CODE, TIMELINESS, \
    VOLUMES, HISTORIES, IDENTITIES, ONE_HUNDRED, SCORE_DATE, RULE_CODES
from app.core.database import get_db
from app.core.exceptions import ScoringException
from app.core.models.cheques import Cheque
from app.core.models.done_trades import DoneTrade
from app.core.models.dtos.cheque_status_dto import ChequesStatusDTO
from app.core.models.dtos.loan_status_dto import LoansStatusDTO
from app.core.models.dtos.score_boundaries_dto import ScoreBoundariesDTO
from app.core.models.dtos.score_change_dto import ScoreChangeDTO
from app.core.models.dtos.score_details_dto import ScoreDetailsDTO
from app.core.models.dtos.score_distribution_dto import ScoreDistributionDTO
from app.core.models.dtos.score_status_dto import ScoreStatusDTO
from app.core.models.dtos.score_time_series_dto import ScoreTimeSeriesDTO
from app.core.models.dtos.user_score_dto import UserScoreDTO
from app.core.models.dtos.vosouq_status_dto import VosouqStatusDTO
from app.core.models.loans import Loan
from app.core.models.profile import Profile
from app.core.models.rules import Rule
from app.core.models.score_changes import ScoreChange
from app.core.models.score_gauges import ScoreGauge
from app.core.models.score_reasons import ScoreReason
from app.core.models.score_time_series import ScoreTimeSeries
from app.core.models.undone_trades import UndoneTrade
from app.core.services.scores_distributions_pipeline_generator import generate_scores_distributions_pipeline
from app.core.services.util import create_score_status_dto, create_vosouq_status_dto, create_loan_status_dto, create_cheque_status_dto, \
    get_zero_if_none, create_score_details_dto, get_second_item, create_score_changes_dto, is_not_none, calculate_dates_diff_by_months_and_days
from app.core.settings import min_score, max_score, distribution_count


class DataService:
    def __init__(self, db: Database = None) -> None:
        super().__init__()
        self.db = get_db() if db is None else db

    # SCORE-GAUGE SERVICES ................................................
    def get_score_gauges(self) -> list:
        return list(self.db.scoreGauges.find())

    def insert_score_gauge(self, sg: ScoreGauge):
        self.db.scoreGauges.insert_one(dict(sg))

    # SCORE-TIME_SERIES SERVICES ................................................
    # Best Model load List Service
    def get_db_score_time_series(self, user_id: int, start_date: date, end_date: date) -> List[ScoreTimeSeries]:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')

        start_date = dateutil.parser.parse(start_date.isoformat())
        end_date = dateutil.parser.parse(end_date.isoformat())
        ret_list = list(
            self.db.scoreTimeSeries.find({USER_ID: user_id, SCORE_DATE: {"$gte": start_date, "$lte": end_date}}))
        return parse_obj_as(List[ScoreTimeSeries], ret_list)

    # RULE SERVICES ........................................................
    def insert_rule(self, r: Rule):
        self.db.rules.insert_one(dict(r))

    def get_rule(self, filter_dict: {}) -> Rule:
        if filter_dict is None:
            raise ScoringException(1, 'filter_dict is empty!')
        return self.db.rules.find_one(filter_dict)

    def get_rules(self, filter_dict: {} = None) -> [Rule]:
        if filter_dict is not None:
            return self.db.rules.find(filter_dict)
        return self.db.rules.find()

    def get_master_rules(self) -> [Rule]:
        r_cursor: Cursor = self.db.rules.find({CODE: {'$in': [IDENTITIES, HISTORIES, VOLUMES, TIMELINESS]}})
        if r_cursor is None:
            return []
        rules: [Rule] = []
        while r_cursor.alive:
            rules.append(Rule.parse_obj(r_cursor.next()))
        return rules

    def delete_rules(self, filter_dict: {}) -> None:
        self.db.rules.delete_many(filter_dict)

    def get_master_rules_boundaries_dict(self):
        rules = self.get_master_rules()
        m_dict: {} = {}
        for r in rules:
            m_dict.__setitem__(r.code, [r.score, r.impact_percent])
        return m_dict

    # PROFILE SERVICES ................................................
    def insert_profile(self, p: Profile):
        if p.membership_date is not None:
            # set min time value to date filed, pydantic model does not support date without time field type
            p.membership_date = datetime.combine(p.membership_date, datetime.min.time())
        self.db.profiles.insert_one(dict(p))

    def update_profile(self, p: Profile):
        if is_not_none(p.membership_date):
            p.membership_date = datetime.combine(p.membership_date, datetime.min.time())
        self.db.profiles.update_one(
            {USER_ID: p.user_id},
            {'$set': dict(p)},
            upsert=False)

    def insert_or_update_profile(self, p: Profile, update_flag: bool = False):
        if update_flag:
            self.update_profile(p)
        else:
            self.insert_profile(p)

    def delete_profiles(self, filter_dict: {}) -> None:
        self.db.profiles.delete_many(filter_dict)

    def get_profiles(self, filter_dict: {}) -> List[Profile]:
        if filter_dict is None:
            raise ScoringException(2, 'filter_dict is empty!')
        dic = self.db.profiles.find(filter_dict)
        if dic is None:
            return []
        return parse_obj_as(List[Profile], dic)

    def get_user_profile(self, user_id: int) -> Profile:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        dic = self.db.profiles.find_one({USER_ID: user_id})
        if dic is None:
            return Profile()
        return Profile.parse_obj(dic)

    def get_users_profiles(self, user_ids: [int]):
        if user_ids is None or len(user_ids) == ZERO:
            raise ScoringException(4, 'user_ids can not be Empty!')
        p_cursor = self.db.profiles.find({USER_ID: {'$in': user_ids}})
        profiles: [Profile] = []
        while p_cursor.alive:
            profiles.append(Profile.parse_obj(p_cursor.next()))
        return profiles

        # DONE-TRADE SERVICES ................................................

    def insert_done_trade(self, dt: DoneTrade):
        self.db.doneTrades.insert_one(dict(dt))

    def update_done_trade(self, dt: DoneTrade):
        self.db.doneTrades.update_one(
            {USER_ID: dt.user_id},
            {'$set': dict(dt)},
            upsert=False)

    def insert_or_update_done_trade(self, dt: DoneTrade, update_flag: bool = False):
        if update_flag:
            self.update_done_trade(dt)
        else:
            self.insert_done_trade(dt)

    def delete_done_trades(self, filter_dict: {}) -> None:
        self.db.doneTrades.delete_many(filter_dict)

    def get_done_trades(self, filter_dict: {}) -> List[DoneTrade]:
        if filter_dict is None:
            raise ScoringException(2, 'filter_dict is empty!')
        dic = self.db.doneTrades.find(filter_dict)
        if dic is None:
            return []
        return parse_obj_as(List[DoneTrade], dic)

    def get_user_done_trade(self, user_id: int) -> DoneTrade:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        dic = self.db.doneTrades.find_one({USER_ID: user_id})
        if dic is None:
            return DoneTrade()
        return DoneTrade.parse_obj(dic)

    # UNDONE-TRADE SERVICES ................................................
    def insert_undone_trade(self, udt: UndoneTrade):
        self.db.undoneTrades.insert_one(dict(udt))

    def update_undone_trade(self, udt: UndoneTrade):
        self.db.undoneTrades.update_one(
            {USER_ID: udt.user_id},
            {'$set': dict(udt)},
            upsert=False)

    def insert_or_update_undone_trade(self, udt: UndoneTrade, update_flag: bool = False):
        if update_flag:
            self.update_undone_trade(udt)
        else:
            self.insert_undone_trade(udt)

    def delete_undone_trades(self, filter_dict: {}) -> None:
        self.db.undoneTrades.delete_many(filter_dict)

    def get_undone_trades(self, filter_dict: {}) -> List[UndoneTrade]:
        if filter_dict is None:
            raise ScoringException(2, 'filter_dict is empty!')
        dic = self.db.undoneTrades.find(filter_dict)
        if dic is None:
            return []
        return parse_obj_as(List[UndoneTrade], dic)

    def get_user_undone_trade(self, user_id: int) -> UndoneTrade:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        dic = self.db.undoneTrades.find_one({USER_ID: user_id})
        if dic is None:
            return UndoneTrade()
        return UndoneTrade.parse_obj(dic)

    # LOAN SERVICES ................................................
    def insert_loan(self, ln: Loan):
        self.db.loans.insert_one(dict(ln))

    def update_loan(self, ln: Loan):
        self.db.loans.update_one(
            {USER_ID: ln.user_id},
            {'$set': dict(ln)},
            upsert=False)

    def insert_or_update_loan(self, ln: Loan, update_flag: bool = False):
        if update_flag:
            self.update_loan(ln)
        else:
            self.insert_loan(ln)

    def delete_loans(self, filter_dict: {}) -> None:
        self.db.loans.delete_many(filter_dict)

    def get_loans(self, filter_dict: {}) -> List[Loan]:
        if filter_dict is None:
            raise ScoringException(2, 'filter_dict is empty!')
        dic = self.db.loans.find(filter_dict)
        if dic is None:
            return []
        return parse_obj_as(List[Loan], dic)

    def get_user_loan(self, user_id: int) -> Loan:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        dic = self.db.loans.find_one({USER_ID: user_id})
        if dic is None:
            return Loan()
        return Loan.parse_obj(dic)

    # CHEQUE SERVICES ................................................
    def insert_cheque(self, ch: Cheque):
        self.db.cheques.insert_one(dict(ch))

    def update_cheque(self, ch: Cheque):
        self.db.cheques.update_one(
            {USER_ID: ch.user_id},
            {'$set': dict(ch)},
            upsert=False)

    def insert_or_update_cheque(self, ch: Cheque, update_flag: bool = False):
        if update_flag:
            self.update_cheque(ch)
        else:
            self.insert_cheque(ch)

    def delete_cheques(self, filter_dict: {}) -> None:
        self.db.cheques.delete_many(filter_dict)

    def get_cheques(self, filter_dict: {}) -> List[Cheque]:
        if filter_dict is None:
            raise ScoringException(2, 'filter_dict is empty!')
        dic = self.db.cheques.find(filter_dict)
        if dic is None:
            return []
        return parse_obj_as(List[Cheque], dic)

    def get_user_cheque(self, user_id: int) -> Cheque:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        dic = self.db.cheques.find_one({USER_ID: user_id})
        if dic is None:
            return Cheque()
        return Cheque.parse_obj(dic)

    # SCORE REASON SERVICES ................................................
    def insert_score_reason(self, scr: ScoreReason):
        self.db.scoreReasons.insert_one(dict(scr))

    def delete_score_reasons(self, filter_dict: {}) -> None:
        self.db.scoreReasons.delete_many(filter_dict)

    def get_score_reason_by_rule_code(self, rule_code: str) -> ScoreReason:
        if rule_code is None:
            raise ScoringException(2, 'rule_code is empty!')
        dic = self.db.scoreReasons.find_one({RULE_CODES: rule_code})
        if dic is None:
            return ScoreReason()
        return ScoreReason.parse_obj(dic)

    # SCORE CHANGE SERVICES ................................................
    def get_user_score_changes(self, user_id: int) -> List[ScoreChange]:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')

        ret_list = list(self.db.scoreChanges.find({USER_ID: user_id}))
        return parse_obj_as(List[ScoreChange], ret_list)

    def insert_score_change(self, sc: ScoreChange):
        self.db.scoreChanges.insert_one(dict(sc))

    # REST SERVICES ................................................
    def get_score_boundaries(self) -> ScoreBoundariesDTO:
        rb = self.get_master_rules_boundaries_dict()
        # calculate max scores boundaries based on max_score
        i_max_score = (max_score * get_second_item(rb.get(IDENTITIES))) // ONE_HUNDRED
        h_max_score = (max_score * get_second_item(rb.get(HISTORIES))) // ONE_HUNDRED
        v_max_score = (max_score * get_second_item(rb.get(VOLUMES))) // ONE_HUNDRED
        t_max_score = (max_score * get_second_item(rb.get(TIMELINESS))) // ONE_HUNDRED
        score_boundaries_dto = ScoreBoundariesDTO(identities_max_score=i_max_score, histories_max_score=h_max_score,
                                                  volumes_max_score=v_max_score, timeliness_max_score=t_max_score,
                                                  min_score=min_score, max_score=max_score)
        return score_boundaries_dto

    def get_score_status(self, user_id: int) -> ScoreStatusDTO:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        pf: Profile = self.get_user_profile(user_id)
        gs = self.get_score_gauges()
        return create_score_status_dto(pf.score, gs, 8, datetime.today())

    def get_vosouq_status(self, user_id: int) -> VosouqStatusDTO:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')

        # load profile
        pf: Profile = self.get_user_profile(user_id)
        if pf.membership_date is None:
            pf.membership_date = date.today()

        # calc membership duration
        membership_duration = calculate_dates_diff_by_months_and_days(
            datetime(year=pf.membership_date.year, month=pf.membership_date.month, day=pf.membership_date.day),
            datetime.today())

        # load & calc doneTrade
        # load doneTrade
        dt: DoneTrade = self.get_user_done_trade(user_id)
        # calc all doneTrades count
        dt_count = get_zero_if_none(dt.timely_trades_count_of_last_3_months) + get_zero_if_none(dt.timely_trades_count_between_last_3_to_12_months) \
                   + get_zero_if_none(dt.past_due_trades_count_of_last_3_months) + get_zero_if_none(dt.past_due_trades_count_between_last_3_to_12_months) \
                   + get_zero_if_none(dt.arrear_trades_count_of_last_3_months) + get_zero_if_none(dt.arrear_trades_count_between_last_3_to_12_months)
        # calc delayed doneTrades count
        delay_days_avg = 0
        if dt_count > 0:
            delayed_dt_count = dt_count - (get_zero_if_none(dt.timely_trades_count_of_last_3_months) + get_zero_if_none(dt.timely_trades_count_between_last_3_to_12_months))
            # calc delayDays' avg
            delay_days_avg = 0 if delayed_dt_count == 0 else dt.total_delay_days // delayed_dt_count

        # calc negativeStatus count
        # todo: this field should be calculated later based on negative_histories which should be provided
        negative_status_count = 0

        # load & calc undoneTrade
        udt: UndoneTrade = self.get_user_undone_trade(user_id)
        # calc all undoneTrades count
        udt_count = get_zero_if_none(udt.undue_trades_count) + get_zero_if_none(udt.past_due_trades_count) + get_zero_if_none(udt.arrear_trades_count)

        # make & return VosouqStatusDTO
        return create_vosouq_status_dto(membership_duration[DAYS],
                                        membership_duration[MONTHS],
                                        dt_count,
                                        udt_count,
                                        negative_status_count,
                                        delay_days_avg,
                                        pf.recommended_to_others_count)

    def get_loans_status(self, user_id: int) -> LoansStatusDTO:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        ln: Loan = self.get_user_loan(user_id)
        return create_loan_status_dto(ln)

    def get_cheques_status(self, user_id: int) -> ChequesStatusDTO:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        ch: Cheque = self.get_user_cheque(user_id)
        return create_cheque_status_dto(ch)

    def get_score_details(self, user_id: int) -> ScoreDetailsDTO:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        pf: Profile = self.get_user_profile(user_id)
        return create_score_details_dto(pf)

    def get_score_distributions(self) -> List[ScoreDistributionDTO]:
        pipeline = generate_scores_distributions_pipeline(min_score, max_score, distribution_count)
        score_distro: CommandCursor = self.db.profiles.aggregate(pipeline)
        score_distro_dict: {} = score_distro.next()
        score_distro_dtos: [ScoreDistributionDTO] = []
        for k in score_distro_dict.keys():
            score_range: [] = k.split(SCORE_DISTRIBUTION_SEPARATOR)
            score_distro_dtos.append(ScoreDistributionDTO(from_score=score_range[ZERO], to_score=score_range[ONE],
                                                          count=score_distro_dict[k]))
        return score_distro_dtos

    def get_score_time_series(self, user_id: int, number_of_days: int) -> List[ScoreTimeSeriesDTO]:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')

        end_date = date.today()
        start_date = end_date - timedelta(number_of_days)
        score_ts: [ScoreTimeSeries] = self.get_db_score_time_series(user_id, start_date, end_date)
        score_changes_dtos: [ScoreTimeSeriesDTO] = []
        for ts in score_ts:
            score_changes_dtos.append(ScoreTimeSeriesDTO(score_date=ts.score_date, score=ts.score))
        return score_changes_dtos

    def get_score_changes(self, user_id: int) -> List[ScoreChangeDTO]:
        if user_id is None:
            raise ScoringException(3, 'user_id can not be None!')
        score_changes: [ScoreChange] = self.get_user_score_changes(user_id)
        scr_dtos: [ScoreChangeDTO] = []
        for sch in score_changes:
            scr_dtos.append(create_score_changes_dto(sch))
        return scr_dtos

    def get_users_scores(self, user_ids: [int]) -> List[UserScoreDTO]:
        if user_ids is None or len(user_ids) == ZERO:
            raise ScoringException(4, 'user_ids can not be Empty!')
        profiles: [Profile] = self.get_users_profiles(user_ids)
        usr_scr_dtos: [UserScoreDTO] = []
        for p in profiles:
            usr_scr_dtos.append(UserScoreDTO(user_id=p.user_id, score=p.score))
        return usr_scr_dtos
