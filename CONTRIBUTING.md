# 贡献指南

感谢你有兴趣为 nologger 做出贡献！

## 开发环境设置

1. 克隆仓库
```bash
git clone https://github.com/isinter/nologger.git
cd nologger
```

2. 安装开发依赖
```bash
pip install -e ".[dev]"
```

## 代码风格

我们使用以下工具来保证代码质量：

- **Black**: 代码格式化工具
- **Flake8**: 代码检查工具
- **MyPy**: 类型检查工具

提交代码前，请确保运行：

```bash
# 格式化代码
black nologger/ tests/

# 检查代码质量
flake8 nologger/ tests/

# 类型检查
mypy nologger/
```

## 测试

运行测试：
```bash
pytest tests/ -v
```

## 提交 Pull Request

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 报告问题

请在 GitHub Issues 中报告任何问题或建议。
