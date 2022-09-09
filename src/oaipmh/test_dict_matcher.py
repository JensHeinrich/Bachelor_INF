from dict_matcher import *

# TODO use proper test framework


assert matching_and_linking_BIO(
    {
        "ABC": "TARGET ABC",
        "ABCD": "TARGET ABCD",
        "AB CD": "TARGET AB CD",
        "AB": "TARGET AB",
        "ABCDABCFGAB": "TARGET ABCDABCFGAB",
    },
    "ABC CD",
    "TEST",
) == (
    ["ABC", "CD"],
    [
        "B-TEST",
        "O",
    ],
    ["TARGET ABC", "", ],
), "Error matching the test string"

assert matching_and_linking_BIO(
    {
        "ABC": "TARGET ABC",
        "ABCD": "TARGET ABCD",
        "AB CD": "TARGET AB CD",
        "AB": "TARGET AB",
        "ABCDABCFGAB": "TARGET ABCDABCFGAB",
    },
    "AB CD",
    "TEST",
) == (
    ["AB", "CD"],
    [
        "B-TEST",
        "I-TEST",
    ],
    ["TARGET AB CD", "", ],
), "Error matching the test string"

assert matching_and_linking_BIO(
    {
        "ABC": "TARGET ABC",
        "ABCD": "TARGET ABCD",
        "AB CD": "TARGET AB CD",
        "AB": "TARGET AB",
        "ABCDABCFGAB": "TARGET ABCDABCFGAB",
    },
    ["ABCDABCFGAB", "CD"],
    "TEST",
) == (
    ["ABCDABCFGAB","CD"],
    [
        "B-TEST",
        "O",
    ],
    ["TARGET ABCDABCFGAB", "",],
), "Error matching the test list"

assert dict_matching(["ABC", "ABCF", "AB", "ADASADASDASDS"], "ABCD") == (
    "ABCD",
    ["positive", "positive", "positive", "unlabeled"],
), "Error matching the test string"
