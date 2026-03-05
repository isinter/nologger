from __future__ import annotations

from contextlib import contextmanager
import contextvars
from typing import Any, Generator, Optional

_trace_id_var = contextvars.ContextVar("nologger_trace_id", default=None)


def set_trace_id(trace_id: Optional[str]) -> Any:
    """
    手动设置当前上下文的 TraceID。
    """
    return _trace_id_var.set(trace_id)


def get_trace_id() -> Optional[str]:
    """
    获取当前上下文的 TraceID。
    """
    return _trace_id_var.get()


def reset_trace_id(token: Any) -> None:
    """
    重置当前上下文的 TraceID。
    """
    _trace_id_var.reset(token)


@contextmanager
def trace_context(trace_id: Optional[str]) -> Generator[None, None, None]:
    """
    上下文管理器，用于自动设置与清理 TraceID。
    """
    token = set_trace_id(trace_id)
    try:
        yield
    finally:
        reset_trace_id(token)
