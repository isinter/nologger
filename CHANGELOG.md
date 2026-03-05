# Changelog

所有重要的项目变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目版本遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [0.3.3] - 2026-03-05

### 改进
- 根据 Python 版本智能选择开发依赖
  - Python 3.8+ 使用最新版本的包
  - Python 3.7 使用兼容的旧版本

## [0.3.2] - 2026-03-05

### 修复
- 降低开发依赖版本以支持 Python 3.7
  - black >=23.1.0
  - flake8 >=6.0.0
  - mypy >=1.0.0
  - pytest >=7.0.0

## [0.3.1] - 2026-03-05

### 修复
- 修复 GitHub Actions CI 配置，优化 Python 版本与 Ubuntu 镜像的搭配
- 为 Python 3.7-3.9 使用 Ubuntu 22.04 镜像
- 为 Python 3.10+ 使用 Ubuntu latest (24.04) 镜像
- 添加 .flake8 配置文件，统一代码检查规则
- 移除未使用的导入

## [0.3.0] - 2026-03-05

### 改进
- 添加了类型注解 (Type Hints) 提升代码可维护性
- 配置了代码质量工具 (Black, Flake8, MyPy)
- 添加了完整的单元测试框架 (tests/)
- 消除了代码重复（统一了 to_log_level 函数）
- 新增项目文档 (CHANGELOG.md, CONTRIBUTING.md)
- 配置 GitHub Actions CI/CD，支持 Python 3.7-3.13
- 添加 PyPI 自动发布工作流
- 优化导入结构和代码格式

## [Unreleased]

## [0.2.2] - 2025-03-04

### 新增
- 配置热加载功能 (Hot Reload)
- TraceID 全链路追踪
- 智能文件轮转（时间 + 大小）
- JSON 结构化日志
- 彩色控制台输出
- 多进程安全写入
- AOP 装饰器 (@log_execution)
- 异常捕获上下文管理器 (logger.catch())

### 特性
- 零配置启动
- 支持从 dict/JSON/YAML/环境变量加载配置
- 自动清理过期日志文件
- 异步非阻塞写入
