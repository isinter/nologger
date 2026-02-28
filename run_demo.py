"""
nologger 功能演示脚本。
涵盖了 JSON 输出、文件轮转、TraceID、装饰器、异常捕获以及配置热加载等场景。
"""
import datetime
import decimal
import json
import os
import time
import uuid

from nologger import get_logger, setup_logger, trace_context


def build_config(console_json=False):
    """构建演示用日志配置，覆盖控制台与文件输出策略。"""
    return {
        "name": "demo",
        "level": "INFO",
        "console": {
            "enabled": True,
            "colored": False,
            "json": console_json,
        },
        "file": {
            "enabled": True,
            "path": "logs/demo.log",
            "json": True,
            "rotation": {
                "when": "S",
                "interval": 5,
                "backupCount": 3,
                "maxBytes": 1024,
            },
            "retention": "1 days",
        },
        "async": {
            "enabled": True,
            "queue_size": 1000,
        },
        "context": {
            "service_name": "demo-service",
        },
    }


def build_payload(index):
    """构建复杂结构化数据，覆盖 datetime/uuid/decimal 等序列化场景。"""
    return {
        "index": index,
        "request_id": uuid.uuid4(),
        "amount": decimal.Decimal("123.45"),
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
        "payload": {
            "user": {"id": 42, "role": "admin"},
            "tags": ["alpha", "beta"],
        },
    }


def emit_rotation_logs(logger, count=40, sleep=0.05):
    """输出多条日志以触发轮转并展示 JSON 字段扁平化。"""
    for index in range(count):
        logger.info("业务日志 %s", index, extra={"extra": build_payload(index)})
        time.sleep(sleep)


def risky_operation():
    """模拟一个会抛异常的业务函数，用于展示 catch 场景。"""
    raise ValueError("模拟的业务异常")


def decorated_task():
    """示例业务函数，展示装饰器记录耗时与返回值。"""
    time.sleep(0.1)
    return {"status": "ok", "cost": 0.1}


def demo_trace_and_decorators(logger):
    """演示 TraceID 注入与装饰器日志记录。"""
    @logger.log_execution(suppress=False, level="INFO")
    def wrapped():
        """被装饰函数，触发装饰器日志。"""
        return decorated_task()

    with trace_context(str(uuid.uuid4())):
        logger.info("开始 Trace 流程", extra={"extra": {"step": "start"}})
        wrapped()
        logger.info("结束 Trace 流程", extra={"extra": {"step": "end"}})


def demo_catch(logger):
    """演示 logger.catch 捕获异常并吞掉错误。"""
    with logger.catch():
        risky_operation()
    logger.info("异常已被 catch 捕获并处理")


def demo_env_level(logger):
    """演示环境变量动态覆盖日志级别。"""
    current_level = os.getenv("ENV_LOG_LEVEL")
    logger.info("当前 ENV_LOG_LEVEL=%s", current_level)


class DemoService:
    """示例服务类，用于验证 logger 在类中的复用能力。"""
    def __init__(self, logger, service_id):
        """初始化服务并绑定 logger。"""
        self.logger = logger
        self.service_id = service_id

    def handle(self, payload):
        """处理请求并记录结构化日志。"""
        self.logger.info(
            "处理请求",
            extra={"extra": {"service_id": self.service_id, "payload": payload}},
        )


def demo_class_instances():
    """演示类中复用 logger、重复实例化与多 logger 使用。"""
    base_config = build_config(console_json=False)
    logger_main = setup_logger(config=base_config)
    logger_same = get_logger("demo")
    service_a = DemoService(logger_main, service_id="A")
    service_b = DemoService(logger_same, service_id="B")
    payload = build_payload(index=100)
    service_a.handle(payload)
    service_b.handle(payload)
    alt_config = build_config(console_json=True)
    alt_config["name"] = "demo-alt"
    alt_config["file"]["path"] = "logs/demo_alt.log"
    alt_config["async"]["enabled"] = False
    logger_alt = setup_logger(config=alt_config)
    service_c = DemoService(logger_alt, service_id="C")
    service_c.handle(build_payload(index=200))


def demo_hot_reload(logger):
    """
    演示配置热加载功能。
    """
    config_file = "temp_config.json"
    initial_config = {
        "level": "DEBUG",
        "console": {"colored": True}
    }
    
    with open(config_file, "w") as f:
        json.dump(initial_config, f)
    
    from nologger import enable_hot_reload, disable_hot_reload
    
    logger.info("启用热加载，监听 %s", config_file)
    enable_hot_reload(config_file, interval=0.1)
    
    logger.debug("这条 DEBUG 日志应该能看到 (级别为 DEBUG)")
    
    # 修改配置
    logger.info("修改配置级别为 INFO...")
    initial_config["level"] = "INFO"
    with open(config_file, "w") as f:
        json.dump(initial_config, f)
    
    # 等待热加载生效
    time.sleep(0.3)
    
    logger.debug("这条 DEBUG 日志不应该看到 (级别已变为 INFO)")
    logger.info("热加载演示完成")
    
    disable_hot_reload()
    if os.path.exists(config_file):
        os.remove(config_file)


def main():
    """运行完整演示，覆盖多场景测试。"""
    config = build_config(console_json=False)
    logger = setup_logger(config=config)

    logger.info("启动演示：控制台文本 + 文件 JSON")
    demo_env_level(logger)
    demo_trace_and_decorators(logger)
    demo_catch(logger)
    
    # 新增：类与实例测试
    service = DemoService(logger, "demo-alt")
    service.handle(200)
    
    # 新增：热加载演示
    demo_hot_reload(logger)
    
    emit_rotation_logs(logger, count=10) # 减少数量，加速演示
    logger.info("演示结束")


if __name__ == "__main__":
    main()
