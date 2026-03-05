import logging
from nologger.utils import to_log_level, parse_retention, flatten_dict


def test_to_log_level():
    assert to_log_level("DEBUG") == logging.DEBUG
    assert to_log_level("info") == logging.INFO
    assert to_log_level(logging.ERROR) == logging.ERROR
    assert to_log_level("UNKNOWN") == logging.INFO


def test_parse_retention():
    assert parse_retention("10 seconds") == 10
    assert parse_retention("5 minutes") == 300
    assert parse_retention("2 hours") == 7200
    assert parse_retention("1 day") == 86400
    assert parse_retention("1 week") == 604800
    assert parse_retention(3600) == 3600
    assert parse_retention(None) is None


def test_flatten_dict():
    data = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    flattened = flatten_dict(data)
    assert flattened == {"a": 1, "b.c": 2, "b.d.e": 3}
