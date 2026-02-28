import datetime
import json
import logging
import os

from .utils import EnhancedJSONEncoder, flatten_dict


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"

    def __init__(self, use_color=True):
        super().__init__("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        self.use_color = use_color

    def format(self, record):
        """
        格式化日志记录，并对控制台输出进行着色。
        """
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        text = super().format(record)

        if not self.use_color:
            return text

        # 对 Traceback 进行增强处理
        if record.exc_text:
            text = self._highlight_traceback(text)

        color = self.COLORS.get(record.levelname, "")
        if not color:
            return text
        return f"{color}{text}{self.RESET}"

    def _highlight_traceback(self, text):
        """
        高亮 Traceback 中的关键信息，缩短标准库路径。
        """
        lines = text.split("\n")
        new_lines = []
        for line in lines:
            # 缩短 Python 标准库路径
            if "Lib\\" in line or "lib/" in line:
                line = line.replace(os.path.dirname(os.__file__), "<STDLIB>")

            # 高亮错误代码行 (通常以 File 开头的行)
            if line.strip().startswith("File "):
                line = f"\033[34m{line}\033[0m"  # 蓝色
            elif "Error:" in line or "Exception:" in line:
                line = f"\033[31;1m{line}\033[0m"  # 红色加粗

            new_lines.append(line)
        return "\n".join(new_lines)


class JSONFormatter(logging.Formatter):
    """
    JSON 格式化器，将日志记录转换为结构化 JSON 字符串。
    """
    def __init__(self, service_name=None, host_ip=None, flatten=True):
        """
        初始化格式化器。
        """
        super().__init__()
        self.service_name = service_name
        self.host_ip = host_ip
        self.flatten = flatten

    def format(self, record):
        """
        将日志记录格式化为 JSON 字符串。
        """
        # 使用时区感知的 datetime 避免弃用警告
        dt = datetime.datetime.fromtimestamp(record.created, datetime.UTC)
        base = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "timestamp_iso": dt.isoformat().replace("+00:00", "Z"),
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "thread": record.thread,
            "process": record.process,
        }
        if self.service_name:
            base["service_name"] = self.service_name
        if self.host_ip:
            base["host_ip"] = self.host_ip
        trace_id = getattr(record, "trace_id", None)
        if trace_id:
            base["trace_id"] = trace_id
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            extra_payload = flatten_dict(extra) if self.flatten else extra
            base.update(extra_payload)
        return json.dumps(base, ensure_ascii=False, cls=EnhancedJSONEncoder)
