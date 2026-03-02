# nologger 技术使用文档

`nologger` 是一个基于 Python 标准库 `logging` 深度封装的增强型日志工具，专为生产环境设计，提供结构化日志、全链路追踪、异步写入和配置热加载等核心功能。

## 🚀 快速开始

### 1. 零配置启动
最简单的使用方式，直接引入并使用默认配置（INFO 级别，控制台着色输出）。

```python
from nologger import logger

logger.info("这是一条普通日志")
logger.error("这是一条错误日志")
```

### 2. 初始化配置
你可以通过 `setup_logger` 手动配置日志行为，支持字典、JSON 或 YAML 格式。

```python
from nologger import setup_logger

config = {
    "name": "my_app",
    "level": "DEBUG",
    "console": {"enabled": True, "colored": True},
    "file": {
        "enabled": True, 
        "path": "logs/app.log", 
        "json": True,
        "rotation": {"when": "D", "interval": 1, "maxBytes": 104857600}
    }
}

logger = setup_logger(config=config)
```

---

## ✨ 核心功能详解

### 1. 结构化日志 (Structured Logging)
默认支持 JSON 格式输出，并自动处理复杂对象（如 `datetime`, `UUID`, `Decimal`）。

```python
import uuid
import decimal
from datetime import datetime

logger.info("处理订单", extra={
    "extra": {
        "order_id": uuid.uuid4(),
        "amount": decimal.Decimal("99.9"),
        "timestamp": datetime.now()
    }
})
```

### 2. 全链路追踪 (TraceID)
支持通过上下文管理器自动注入 `trace_id`，方便跨函数、跨模块追踪请求。

```python
from nologger import trace_context
import uuid

with trace_context(str(uuid.uuid4())):
    logger.info("步骤 1：开始处理")
    # ... 业务逻辑 ...
    logger.info("步骤 2：处理完成")
```

### 3. AOP 装饰器
使用 `@log_execution` 自动记录函数的入参、出参、执行耗时及异常信息。

```python
@logger.log_execution(level="INFO")
def process_data(data):
    # 执行一些业务逻辑
    return {"status": "success"}
```

### 4. 异常捕获 (logger.catch)
优雅地捕获代码块内的异常，记录堆栈信息并防止程序崩溃。

```python
with logger.catch():
    1 / 0  # 这里的异常会被自动记录并吞掉
```

### 5. 增强型控制台体验
- **语义化着色**：不同日志级别显示不同颜色。
- **Traceback 优化**：自动高亮错误代码行，并缩短 Python 标准库路径。

### 6. 智能轮转配置 (Smart Rotation)

`nologger` 支持时间与大小双向轮转。

```python
config = {
    "file": {
        "path": "logs/app.log",
         "rotation": {
             "when": "H",            # 轮转颗粒度: S, M, H, D, W, midnight
             "interval": 1,          # 轮转间隔
             "backup_count": 7,       # 保留的历史文件数
             "max_bytes": 10*1024*1024 # 单文件最大字节数 (如 10MB)
         },
        "retention": "30 days"      # 自动清理保留时间 (支持 seconds, minutes, hours, days, weeks)
    }
}
```

*   **多维度轮转：** 如果设置了 `maxBytes`，即使未到指定时间（如一小时），只要文件大小超限也会触发轮转。
*   **防止覆盖：** 在同一时间段内触发多次轮转时，会自动追加序号（如 `app.2026-03-02.1.log`），确保日志不丢失。
*   **并发安全：** 内置文件锁，解决 Windows/Linux 下多进程写入冲突。

### 7. 配置热加载 (Hot Reload)
支持在程序运行时动态监听配置文件变化并更新日志级别或格式，无需重启服务。

```python
from nologger import enable_hot_reload

# 监听 config.json，每 1 秒检查一次
enable_hot_reload("config.json", interval=1.0)
```

---

## 🛠️ 配置项说明

| 配置项 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `name` | Logger 名称 | `nologger` |
| `level` | 日志级别 (DEBUG/INFO/ERROR 等) | `INFO` |
| `console.enabled` | 是否开启控制台输出 | `True` |
| `console.json` | 控制台是否使用 JSON 格式 | `False` |
| `file.enabled` | 是否开启文件输出 | `False` |
| `file.path` | 日志文件路径 | `logs/app.log` |
| `file.retention` | 日志保留策略 (如 "7 days") | `None` |
| `async.enabled` | 是否开启异步非阻塞写入 | `False` |

---

## 📝 最佳实践
1. **生产环境**：建议开启 `file.json=True` 和 `async.enabled=True` 以获得最高性能和易于采集的日志。
2. **开发环境**：建议开启 `console.colored=True` 以获得直观的调试体验。
3. **微服务**：务必在入口处使用 `trace_context` 注入请求 ID。
