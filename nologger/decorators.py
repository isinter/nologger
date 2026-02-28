import functools
import logging
import time


def log_execution(logger, suppress=False, level="INFO"):
    """
    函数执行装饰器，自动记录入参、出参、耗时及异常。
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            log_level = _to_level(level)
            logger.log(log_level, "开始执行 %s", func.__name__, extra={"extra": {"args": args, "kwargs": kwargs}})
            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start
                logger.log(log_level, "完成执行 %s", func.__name__, extra={"extra": {"elapsed": elapsed, "result": result}})
                return result
            except Exception:
                elapsed = time.perf_counter() - start
                logger.exception("执行异常 %s", func.__name__, extra={"extra": {"elapsed": elapsed}})
                if suppress:
                    return None
                raise
        return wrapper
    return decorator


def _to_level(level):
    """
    将字符串或整数转换为标准 logging 级别。
    """
    if isinstance(level, int):
        return level
    return logging._nameToLevel.get(str(level).upper(), logging.INFO)
