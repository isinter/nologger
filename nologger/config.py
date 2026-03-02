import json
import os


DEFAULT_CONFIG = {
    "name": "nologger",
    "level": "INFO",
    "console": {
        "enabled": True,
        "colored": True,
        "json": False,
    },
    "file": {
        "enabled": False,
        "path": "logs/app.log",
        "json": True,
        "rotation": {
            "when": "D",
            "interval": 1,
            "backup_count": 7,
            "max_bytes": 100 * 1024 * 1024,
        },
        "retention": "30 days",
    },
    "async": {
        "enabled": False,
        "queue_size": 10000,
    },
    "context": {
        "service_name": None,
    },
}


def deep_merge(base, override):
    """
    深度合并两个字典配置。
    """
    result = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config=None, config_path=None, use_env=True):
    """
    加载并合并多源配置 (默认配置、文件配置、手动配置及环境变量)。
    """
    cfg = dict(DEFAULT_CONFIG)
    if config_path:
        cfg = deep_merge(cfg, load_config_file(config_path))
    if config:
        cfg = deep_merge(cfg, config)
    if use_env:
        level = os.getenv("ENV_LOG_LEVEL")
        if level:
            cfg["level"] = level
    return cfg


def load_config_file(path):
    """
    从指定路径加载 JSON 或 YAML 配置文件。
    """
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8") as f:
        if ext in [".json"]:
            return json.load(f)
        if ext in [".yaml", ".yml"]:
            try:
                import yaml
            except Exception as exc:
                raise RuntimeError("需要安装 PyYAML 才能加载 YAML 配置") from exc
            return yaml.safe_load(f) or {}
        return json.load(f)
