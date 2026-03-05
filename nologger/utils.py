from __future__ import annotations

import datetime
import decimal
import json
import logging
import os
import re
import socket
import uuid
from typing import Any, Dict, Optional, Union


def to_log_level(level: Union[str, int]) -> int:
    """
    将字符串或整数转换为标准 logging 级别。
    """
    if isinstance(level, int):
        return level
    return logging._nameToLevel.get(str(level).upper(), logging.INFO)


def ensure_dir(path: str) -> None:
    """
    确保文件所在的目录存在。
    """
    directory = os.path.dirname(os.path.abspath(path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def parse_retention(retention: Optional[Union[str, int, float]]) -> Optional[int]:
    """
    解析保留时间字符串 (如 "30 days") 为秒数。
    """
    if not retention:
        return None
    if isinstance(retention, (int, float)):
        return int(retention)
    text = str(retention).strip().lower()
    pattern = r"^\s*(\d+)\s*(seconds|second|minutes|minute|hours|hour|days|day|weeks|week)\s*$"
    match = re.match(pattern, text)
    if not match:
        return None
    value = int(match.group(1))
    unit = match.group(2)
    seconds_map = {
        "second": 1,
        "seconds": 1,
        "minute": 60,
        "minutes": 60,
        "hour": 3600,
        "hours": 3600,
        "day": 86400,
        "days": 86400,
        "week": 604800,
        "weeks": 604800,
    }
    return value * seconds_map[unit]


def flatten_dict(data: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """
    将嵌套字典展平为单层字典，键名用 sep 连接。
    """
    items: Dict[str, Any] = {}
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else str(key)
        if isinstance(value, dict):
            items.update(flatten_dict(value, new_key, sep=sep))
        else:
            items[new_key] = value
    return items


class EnhancedJSONEncoder(json.JSONEncoder):
    """
    增强型 JSON 编码器，支持 datetime、UUID、Decimal 等类型。
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def to_json(data: Any) -> str:
    """
    将对象序列化为 JSON 字符串，支持增强类型。
    """
    return json.dumps(data, ensure_ascii=False, cls=EnhancedJSONEncoder)


def get_host_ip() -> Optional[str]:
    """
    获取本机 IP 地址。
    """
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return None
