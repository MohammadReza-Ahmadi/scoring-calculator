from datetime import date, datetime

import jdatetime
from pymongo.command_cursor import CommandCursor

from app.core.constants import ZERO, PERSIAN_LOCALE
from app.core.database import get_db
from app.core.exceptions import ScoringException
from app.core.services.util import convert_date_to_milliseconds_since_epoch
from app.core.settings import min_score, max_score

score_changes_max_in_month_interval_pipeline_sample = [
    {
        "$facet": {
            "month1": [
                {
                    "$match": {
                        "change_date": {
                            "$gt": "new Date('2021-02-01T00:00:00Z')",
                            "$lte": "new Date('2021-02-13T00:00:00Z')"
                        }
                    }
                },
                {
                    "$bucket": {
                        "groupBy": "$score",
                        "boundaries": [0, 1000],
                        "default": "ALL",
                        "output": {
                            "count": {"$sum": 1},
                            "max_score": {"$max": "$score"},
                        }
                    }
                },
                {
                    "$project":
                        {"_id": 0}
                }
            ],

            "month2": [
                {
                    "$match": {
                        "change_date": {
                            "$gt": "new Date('2021-02-14T00:00:00Z')",
                            "$lte": "new Date('2021-02-28T00:00:00Z')"
                        }
                    }
                },
                {
                    "$bucket": {
                        "groupBy": "$score",
                        "boundaries": [0, 1000],
                        "default": "ALL",
                        "output": {
                            "count": {"$sum": 1},
                            "max_score": {"$max": "$score"},
                        }
                    }
                },
                {
                    "$project":
                        {"_id": 0}
                }
            ]
        }
    }
]


def generate_score_changes_max_in_month_interval_pipeline(dates: list):
    if dates is None:
        raise ScoringException(5, 'dates list can not be None!')

    if len(dates) < 2:
        raise ScoringException(5, 'dates list should be have at least 2 items!')

    dates.sort()
    pipeline = []
    facet_dict = {}
    start_date = dates[ZERO]
    key = "month"

    for i in range(1, len(dates)):
        facet_dict_array_items = [
            get_facet_dict_match_item(start_date, dates[i]),  # add facet match item
            get_facet_dict_bucket_item(min_score, max_score),  # add facet bucket item
            get_bucket_project_item()  # add facet' bucket project item
        ]
        # facet_dict.__setitem__((key + str(i)), facet_dict_array_items)
        facet_dict.__setitem__(str(start_date.isoformat()), facet_dict_array_items)
        start_date = dates[i]

    pipeline.append({"$facet": facet_dict})
    return pipeline


def get_facet_dict_match_item(start_date: date, end_date: date):
    return {
        "$match": {
            "change_date": {
                # "$gt": dateutil.parser.parse(start_date.isoformat()),
                # "$lte": dateutil.parser.parse(end_date.isoformat())
                "$gt": generate_score_changes_max_in_month_interval_pipeline(start_date),
                "$lte": generate_score_changes_max_in_month_interval_pipeline(end_date)
            }
        }
    }


# noinspection PyShadowingNames
def get_facet_dict_bucket_item(min_score: int, max_score: int):
    return {
        "$bucket": {
            "groupBy": "$score",
            "boundaries": [min_score, max_score],
            "default": "ALL",
            "output": {
                "max_score": {"$max": "$score"},
            }
        }
    }


def get_bucket_project_item():
    return {
        "$project":
            {"_id": 0}
    }


if __name__ == '__main__':
    dates = [
        jdatetime.date(1399, 11, 13, locale=PERSIAN_LOCALE).togregorian(),
        jdatetime.date(1399, 11, 19, locale=PERSIAN_LOCALE).togregorian(),
        jdatetime.date(1399, 11, 24, locale=PERSIAN_LOCALE).togregorian(),
        # jdatetime.date(1398, 11, 29, locale=PERSIAN_LOCALE).togregorian(),
        # jdatetime.date(1398, 12, 4, locale=PERSIAN_LOCALE).togregorian(),
        # jdatetime.date(1398, 12, 9, locale=PERSIAN_LOCALE).togregorian(),

    ]
    # dt_time = datetime.now()
    dt_time = datetime(year=2021, month=2, day=2, hour=13, minute=23, second=59)
    print('now={}'.format(dt_time))
    # to_int_1 = int(round(dt_time.timestamp() * 1000))
    to_int_1 = convert_date_to_milliseconds_since_epoch(dt_time)
    print('to_int_1:{}'.format(to_int_1))
    f = 10000 * dt_time.year + 100 * dt_time.month + dt_time.day
    print('to_int_2:{}'.format(f))
    pipeline = generate_score_changes_max_in_month_interval_pipeline(dates)
    r: CommandCursor = get_db().get_collection('scoreChanges').aggregate(pipeline)
    r_dict: {} = r.next()
    for k in r_dict.keys():
        print('{}:{}'.format(k, r_dict[k]))
