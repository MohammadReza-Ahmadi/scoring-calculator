from enum import IntEnum


class ProfileMilitaryServiceStatusEnum(IntEnum):
    UNKNOWN = 0     # نامشخص
    FINISHED = 1    # پایان خدمت
    EXEMPTED = 2    # معافیت
    ONGOING = 3     # درحال خدمت
    SUBJECTED = 4   # مشمول غیر غایب
    ABSENT = 5      # غایب
