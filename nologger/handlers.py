import logging
from logging.handlers import TimedRotatingFileHandler
import os
import time

from .utils import ensure_dir, parse_retention


def _lock_stream(stream):
    """
    对流进行加锁，支持 Windows 和 Unix。
    """
    if stream is None:
        return
    try:
        fd = stream.fileno()
    except Exception:
        return
    if os.name == "nt":
        try:
            import msvcrt
            # 锁定 1 字节即可，仅作为并发写入的标志
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        except Exception:
            pass
    else:
        try:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
        except Exception:
            pass


def _unlock_stream(stream):
    """
    释放流上的锁。
    """
    if stream is None:
        return
    try:
        fd = stream.fileno()
    except Exception:
        return
    if os.name == "nt":
        try:
            import msvcrt
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except Exception:
            pass
    else:
        try:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_UN)
        except Exception:
            pass


def cleanup_old_logs(log_path, retention):
    """
    根据保留策略清理旧日志文件。
    支持优雅的命名规则：匹配 app.log, app.YYYY-MM-DD.log, app.N.log
    """
    seconds = parse_retention(retention)
    if not seconds:
        return
    directory = os.path.dirname(os.path.abspath(log_path))
    base_full = os.path.basename(log_path)
    base_name, base_ext = os.path.splitext(base_full)
    
    if not os.path.isdir(directory):
        return
    now = time.time()
    for filename in os.listdir(directory):
        # 匹配逻辑：
        # 1. 以 base_name 开头
        # 2. 以 base_ext 结尾
        if not (filename.startswith(base_name) and filename.endswith(base_ext)):
            continue
        
        full_path = os.path.join(directory, filename)
        try:
            mtime = os.path.getmtime(full_path)
        except Exception:
            continue
        if now - mtime > seconds:
            try:
                os.remove(full_path)
            except Exception:
                pass


class SmartRotatingFileHandler(TimedRotatingFileHandler):
    """
    支持时间与大小双向轮转的增强型日志处理器。
    支持优雅的命名规则：轮转后的文件名保留扩展名 (如 app.2026-02-28.log)。
    """
    def __init__(
        self,
        filename,
        when="D",
        interval=1,
        backup_count=7,
        max_bytes=0,
        encoding="utf-8",
        delay=True,
        utc=False,
        retention=None,
    ):
        """
        初始化处理器，支持自动创建目录。
        """
        ensure_dir(filename)
        super().__init__(
            filename,
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding=encoding,
            delay=delay,
            utc=utc,
        )
        self.max_bytes = max_bytes
        self.retention = retention
        # 设置自定义命名规则
        self.namer = self._elegant_namer
        cleanup_old_logs(self.baseFilename, self.retention)

    def _elegant_namer(self, default_name):
        """
        优雅的命名规则转换。
        输入: logs/app.log.2026-02-28 或 logs/app.log.1
        输出: logs/app.2026-02-28.log 或 logs/app.1.log
        """
        if not default_name.startswith(self.baseFilename):
            return default_name
            
        # 获取后缀 (如 .2026-02-28 或 .1)
        suffix = default_name[len(self.baseFilename):]
        if not suffix:
            return default_name
            
        # 去掉前导点
        if suffix.startswith("."):
            suffix = suffix[1:]
            
        # 分离原文件名的基名和扩展名
        base, ext = os.path.splitext(self.baseFilename)
        return f"{base}.{suffix}{ext}"

    def shouldRollover(self, record):
        """
        判断是否需要进行文件轮转。
        """
        if self.stream is None:
            self.stream = self._open()
        # 优先判断父类的基于时间的轮转
        if super().shouldRollover(record):
            return 1
        # 增加基于大小的轮转判断
        if self.max_bytes > 0:
            try:
                self.stream.seek(0, os.SEEK_END)
                if self.stream.tell() + len(self.format(record)) >= self.max_bytes:
                    return 1
            except Exception:
                return 0
        return 0

    def doRollover(self):
        """
        执行轮转操作。
        如果目标文件名已存在（通常是因为在同一个时间间隔内触发了多次基于大小的轮转），
        则自动增加序号后缀 (如 app.2026-03-02.1.log)。
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # 计算基于时间的标准后缀
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime).tm_isdst
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple.tm_isdst
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        
        # 基础后缀 (例如 2026-02-28)
        base_suffix = time.strftime(self.suffix, timeTuple)
        
        # 构造目标文件名
        base, ext = os.path.splitext(self.baseFilename)
        dfn = f"{base}.{base_suffix}{ext}"
        
        # 如果文件已存在，则优先使用当前精确时间戳以避免大量序号文件
        if os.path.exists(dfn):
            if self.utc:
                precise_suffix = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(currentTime))
            else:
                precise_suffix = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(currentTime))
            dfn_precise = f"{base}.{precise_suffix}{ext}"
            if not os.path.exists(dfn_precise):
                dfn = dfn_precise
            else:
                # 若仍冲突，再回退到递增序号以保证唯一性
                i = 1
                while True:
                    dfn_seq = f"{base}.{base_suffix}.{i}{ext}"
                    if not os.path.exists(dfn_seq):
                        dfn = dfn_seq
                        break
                    i += 1
        
        # 执行重命名
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            
        # 清理旧日志
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        
        if not self.delay:
            self.stream = self._open()
            
        # 更新下次轮转时间
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        
        # 处理夏令时切换
        if not self.utc:
            dstCheckAt = newRolloverAt - self.interval
            if time.localtime(dstCheckAt).tm_isdst != time.localtime(newRolloverAt).tm_isdst:
                if time.localtime(dstCheckAt).tm_isdst:
                    addend = 3600
                else:
                    addend = -3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
        
        cleanup_old_logs(self.baseFilename, self.retention)

    def emit(self, record):
        """
        写入单条日志，并在 Windows 下处理并发权限异常。
        """
        try:
            _lock_stream(self.stream)
            try:
                super().emit(record)
            finally:
                _unlock_stream(self.stream)
        except (PermissionError, RuntimeError):
            # Windows 轮转时可能发生 PermissionError
            # 简单处理：跳过或尝试重新打开
            pass
