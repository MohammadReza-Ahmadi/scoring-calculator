from app.core.constants import SCORE_DISTRIBUTION_SEPARATOR, COUNT_KEY
from app.core.exceptions import ScoringException

scores_distributions_pipeline_sample = [
    {
        "$facet":
            {
                "0_to_50":
                    [
                        {"$match": {"score": {"$gte": 0, "$lte": 50}}},
                        {"$count": "cnt"}
                    ],
                "51_to_100":
                    [
                        {"$match": {"score": {"$gte": 51, "$lte": 100}}},
                        {"$count": "cnt"}
                    ]
            }
    },
    {
        "$project":
            {
                "0_to_50": {"$arrayElemAt": ["$0_to_50.cnt", 0]},
                "51_to_100": {"$arrayElemAt": ["$51_to_100.cnt", 0]}
            }
    }
]


def generate_scores_distributions_pipeline(min_score: int, max_score: int, distribution_count: int):
    if max_score == 0:
        raise ScoringException(4, 'maxScore cannot be zero!')
    if min_score >= max_score:
        raise ScoringException(4, 'minScore cannot be bigger or equal maxScore!')
    if distribution_count == 0 and distribution_count > max_score:
        raise ScoringException(4, 'step cannot be zero or bigger than maxScore!')

    step = (max_score - min_score) // distribution_count
    start = min_score
    end = start + step
    pipeline = []
    facet_dict = {}
    project_dict = {}

    for i in range(distribution_count):
        # add facet part items
        key = str(start) + SCORE_DISTRIBUTION_SEPARATOR + str(end)
        f_dict_first_item: {} = get_facet_dict_match_item(start, end)
        f_dict_second_item: {} = {"$count": COUNT_KEY}
        facet_dict_array_items = [f_dict_first_item, f_dict_second_item]
        facet_dict.__setitem__(key, facet_dict_array_items)

        # add project part items
        p_dict_item = get_project_dict_item(start, end)
        project_dict.__setitem__(key, p_dict_item)
        start = end + 1
        end = (start + step - 1) if i < (distribution_count - 2) else max_score

    pipeline.append({"$facet": facet_dict})
    pipeline.append({"$project": project_dict})
    return pipeline


def get_facet_dict_match_item(start: int, end: int):
    return {"$match": {"score": {"$gte": start, "$lte": end}}}


def get_project_dict_item(start: int, end: int):
    return {"$arrayElemAt": ["$" + str(start) + SCORE_DISTRIBUTION_SEPARATOR + str(end) + "." + COUNT_KEY, 0]}
