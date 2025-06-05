from enum import Enum


class Configuration(Enum):
    COLUMNS = "Columns"

    # Data type constraints for columns
    DATA_TYPE = "DataType"
    INT_MIN = "IntMin"
    INT_MAX = "IntMax"
    FLOAT_MIN = "FloatMin"
    FLOAT_MAX = "FloatMax"
    STRING_MAX = "StringMax"
    DATE_MIN = "DateMin"
    DATE_MAX = "DateMax"
    CATEGORIES = "Categories"

    # General cleaning options
    DELETE_DUPLICATES = "DeleteDuplicates"
    DROP_MISSING = "DropMissing"
    IMPUTE_MISSING_MEAN = "ImputeMissingMean"
    IMPUTE_MISSING_MEDIAN = "ImputeMissingMedian"

    # Analytics options
    ANALYZE_DISTRIBUTION = "AnalyzeDistribution"
    ANALYZE_OUTLIERS = "AnalyzeOutliers"
    ANALYZE_MISSINGNESS = "AnalyzeMissingness"
    ANALYZE_CATEGORIES = "AnalyzeCategories"
    ANALYZE_UNITS = "AnalyzeUnits"
