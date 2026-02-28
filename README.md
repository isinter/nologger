# nologger

> **—— 专为生产环境设计的 Python 全栈日志解决方案**

## 📖 简介

**[nologger]** 是基于 Python 标准库 `logging` 深度封装的增强型日志工具。它解决了原生 logging 配置繁琐、JSON 序列化困难及多进程写入不安全等痛点。旨在通过一行代码实现从“控制台开发调试”到“生产环境结构化采集”的无缝切换。

## ✨ 核心特性 (Key Features)

### 1. 🚀 零配置启动与配置热加载 (Zero-Config & Hot Reload)
*   **默认最佳实践：** 引入即用，默认开启 `INFO` 级别与标准化控制台格式，无需编写繁琐的 `formatter/handler` 代码。
*   **多源配置加载：** 支持从 `dict`、`JSON`、`YAML` 文件或环境变量 (`ENV_LOG_LEVEL`) 加载配置，适应容器化部署。
*   **配置热更新：** （可选高级功能）支持监听配置文件变化，无需重启服务即可动态调整日志级别。

### 2. 🎨 沉浸式控制台体验 (Developer Experience)
*   **语义化着色：** 对不同级别（`DEBUG`/`INFO`/`ERROR`）及关键字段（时间、模块名）进行 ANSI 智能着色，视觉干扰降至最低。
*   **异常高亮：** 优化 `Traceback` 显示，自动缩短标准库冗长路径，高亮错误代码行，让调试聚焦核心逻辑。

### 3. 💾 企业级文件管理 (Advanced File Management)
*   **智能轮转 (Smart Rotation)：** 同时支持 `TimeBased`（按天/小时）和 `SizeBased`（按 100MB）的双重切割策略。
*   **自动清理 (Retention Policy)：** 内置过期清理机制（例如：`retention="30 days"`），自动删除陈旧日志文件，防止磁盘写满。
*   **多进程安全：** 集成文件锁或多进程安全的 Handler，彻底解决多进程并发写入时的日志丢失与文件错乱问题。

### 4. 📊 结构化与序列化 (Structured & Serialization)
*   **JSON First：** 一键切换至 JSON 模式，自动展平嵌套对象。
*   **智能序列化：** 内置增强型 Encoder，自动处理 `datetime`、`UUID`、`Decimal` 及自定义 Object，不仅是记录字符串，更是记录数据。
*   **标准化字段：** 自动注入 `service_name`、`host_ip`、`timestamp_iso`，完美适配 ELK (Elasticsearch)、Splunk 或 Filebeat 采集标准。

### 5. 🕵️ 上下文感知与全链路追踪 (Context & Tracing)
*   **自动化元数据：** 每一条日志自动携带 `filename`、`lineno`、`funcName` 及 `thread/process_id`。
*   **TraceID 注入：** 支持通过 `ContextVar` 传递 `Trace-ID`，将同一个请求跨越多层调用的日志串联起来，解决微服务/异步任务难以追踪的问题。

### 6. 🛠️ AOP 切面与装饰器 (Decorators & Hooks)
*   **`@log_execution` 装饰器：**
    *   **全景记录：** 自动记录函数入参 (`args/kwargs`)、返回值、执行耗时及异常信息。
    *   **异常保护：** 可配置 `suppress=True` 模式，在记录错误日志的同时吞掉异常，防止非关键逻辑（如发通知）导致主程序崩溃。
*   **上下文管理器：** 使用 `with logger.catch():` 优雅地捕获代码块内的所有潜在错误。

### 7. ⚡ 异步非阻塞架构 (Async & High Performance)
*   **后台队列写入：** 采用 `QueueHandler` + `QueueListener` 模式，将日志写入操作从主业务线程剥离。
*   **低延迟保证：** 在高并发场景下（QPS > 5000），确保业务逻辑不受磁盘 IO 抖动影响，真正做到“日志记录零感知的”。