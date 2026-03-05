import os
import tempfile
from nologger.config import load_config, deep_merge, DEFAULT_CONFIG


def test_deep_merge():
    base = {"a": 1, "b": {"c": 2}}
    override = {"b": {"d": 3}, "e": 4}
    merged = deep_merge(base, override)
    assert merged["a"] == 1
    assert merged["b"]["c"] == 2
    assert merged["b"]["d"] == 3
    assert merged["e"] == 4


def test_load_config_default():
    cfg = load_config()
    assert cfg["name"] == "nologger"
    assert cfg["level"] == "INFO"
    assert cfg["console"]["enabled"] is True


def test_load_config_with_dict():
    cfg = load_config(config={"level": "DEBUG"})
    assert cfg["level"] == "DEBUG"
    assert cfg["name"] == "nologger"


def test_load_config_from_env():
    os.environ["ENV_LOG_LEVEL"] = "WARNING"
    cfg = load_config(use_env=True)
    assert cfg["level"] == "WARNING"
    del os.environ["ENV_LOG_LEVEL"]
