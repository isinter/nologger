import atexit
import logging
import queue
import threading
import time
from logging.handlers import QueueHandler, QueueListener

from .config import load_config
from .context import get_trace_id
from .decorators import log_execution
from .formatter import ColorFormatter, JSONFormatter
from .handlers import SmartRotatingFileHandler
from .utils import get_host_ip


_listener = None
_configured = False
_hot_reload_thread = None
_hot_reload_stop = threading.Event()


class ContextFilter(logging.Filter):
    """
    日志过滤器，用于自动向日志记录中注入上下文元数据（如 TraceID、服务名）。
    """
    def __init__(self, service_name=None):
        super().__init__()
        self.service_name = service_name

    def filter(self, record):
        record.trace_id = get_trace_id()
        record.service_name = self.service_name
        return True


class Nologger:
    """
    增强型日志对象包装器，提供 catch 和 log_execution 等额外功能。
    """
    def __init__(self, logger):
        self.logger = logger

    def __getattr__(self, item):
        return getattr(self.logger, item)

    def catch(self):
        """
        异常捕获上下文管理器。
        """
        return _logger_catch(self.logger)

    def log_execution(self, suppress=False, level="INFO"):
        """
        函数执行装饰器。
        """
        return log_execution(self.logger, suppress=suppress, level=level)


def _logger_catch(logger):
    """
    内部异常捕获实现。
    """
    class _Catch:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            if exc_type is not None:
                logger.exception("捕获异常")
                return True
            return False
    return _Catch()


def setup_logger(config=None, config_path=None, use_env=True, name=None):
    """
    全局日志初始化配置入口。
    """
    global _listener, _configured
    cfg = load_config(config=config, config_path=config_path, use_env=use_env)
    logger_name = name or cfg.get("name") or "nologger"
    logger = logging.getLogger(logger_name)
    logger.setLevel(_to_level(cfg.get("level", "INFO")))
    logger.propagate = False
    if _configured:
        logger.handlers.clear()
    handlers = _build_handlers(cfg)
    for handler in handlers:
        logger.addHandler(handler)
    logger.addFilter(ContextFilter(service_name=cfg.get("context", {}).get("service_name")))
    async_cfg = cfg.get("async", {})
    if async_cfg.get("enabled"):
        q = queue.Queue(maxsize=async_cfg.get("queue_size", 10000))
        queue_handler = QueueHandler(q)
        listener = QueueListener(q, *handlers, respect_handler_level=True)
        listener.start()
        _listener = listener
        logger.handlers.clear()
        logger.addHandler(queue_handler)
        atexit.register(_stop_listener)
    _configured = True
    return Nologger(logger)


def get_logger(name=None):
    """
    获取已配置的日志实例。
    """
    base = logging.getLogger(name or "nologger")
    return Nologger(base)


def enable_hot_reload(config_path, interval=1.0, use_env=True):
    """
    开启配置文件热加载监听。
    """
    global _hot_reload_thread
    if _hot_reload_thread and _hot_reload_thread.is_alive():
        return
    _hot_reload_stop.clear()

    def _watch():
        last_mtime = None
        while not _hot_reload_stop.is_set():
            try:
                mtime = os.path.getmtime(config_path)
                if last_mtime is None:
                    last_mtime = mtime
                elif mtime != last_mtime:
                    setup_logger(config_path=config_path, use_env=use_env)
                    last_mtime = mtime
            except Exception:
                pass
            time.sleep(interval)

    import os
    thread = threading.Thread(target=_watch, name="nologger-hot-reload", daemon=True)
    thread.start()
    _hot_reload_thread = thread


def disable_hot_reload():
    """
    停止热加载监听。
    """
    _hot_reload_stop.set()


def _build_handlers(cfg):
    """
    内部方法：根据配置构建 Handler 列表。
    """
    handlers = []
    console_cfg = cfg.get("console", {})
    if console_cfg.get("enabled", True):
        console_handler = logging.StreamHandler()
        if console_cfg.get("json"):
            console_handler.setFormatter(_json_formatter(cfg))
        else:
            console_handler.setFormatter(ColorFormatter(use_color=console_cfg.get("colored", True)))
        console_handler.setLevel(_to_level(cfg.get("level", "INFO")))
        handlers.append(console_handler)
    file_cfg = cfg.get("file", {})
    if file_cfg.get("enabled"):
        rotation = file_cfg.get("rotation", {})
        # 兼容旧配置键（小驼峰）与新配置键（下划线）
        backup_count = rotation.get("backup_count", rotation.get("backupCount", 7))
        max_bytes = rotation.get("max_bytes", rotation.get("maxBytes", 100 * 1024 * 1024))
        file_handler = SmartRotatingFileHandler(
            file_cfg.get("path", "logs/app.log"),
            when=rotation.get("when", "D"),
            interval=rotation.get("interval", 1),
            backup_count=backup_count,
            max_bytes=max_bytes,
            retention=file_cfg.get("retention"),
        )
        if file_cfg.get("json", True):
            file_handler.setFormatter(_json_formatter(cfg))
        else:
            file_handler.setFormatter(ColorFormatter(use_color=False))
        file_handler.setLevel(_to_level(cfg.get("level", "INFO")))
        handlers.append(file_handler)
    return handlers


def _json_formatter(cfg):
    """
    内部方法：构建 JSON 格式化器。
    """
    service_name = cfg.get("context", {}).get("service_name")
    host_ip = get_host_ip()
    return JSONFormatter(service_name=service_name, host_ip=host_ip)


def _to_level(level):
    """
    内部方法：转换日志级别。
    """
    if isinstance(level, int):
        return level
    return logging._nameToLevel.get(str(level).upper(), logging.INFO)


def _stop_listener():
    """
    内部方法：停止异步监听器并释放资源。
    """
    global _listener
    if _listener:
        try:
            _listener.stop()
        finally:
            _listener = None
