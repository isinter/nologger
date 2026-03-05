"""
nologger - 专为生产环境设计的 Python 全栈日志解决方案。
"""

from .core import setup_logger, get_logger, enable_hot_reload, disable_hot_reload, Nologger
from .context import set_trace_id, get_trace_id, reset_trace_id, trace_context
from .decorators import log_execution

logger = setup_logger()

__all__ = [
    "setup_logger",
    "get_logger",
    "enable_hot_reload",
    "disable_hot_reload",
    "set_trace_id",
    "get_trace_id",
    "reset_trace_id",
    "trace_context",
    "log_execution",
    "Nologger",
    "logger",
]
