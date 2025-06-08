from enum import Enum


class Operation(Enum):
    DROP_MISSING = "DropMissing"
    IMPUTE_MEAN = "ImputeMean"
    IMPUTE_MEDIAN = "ImputeMedian"
    IMPUTE_MODE = "ImputeMode"

    DROP_UPPER = "DropUpper"
    DROP_LOWER = "DropLower"

    STANDARDIZE = "Standardize"

    CORRECT_CATEGORIES = "CorrectCategories"
