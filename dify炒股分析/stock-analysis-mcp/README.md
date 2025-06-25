# 股票分析 MCP 工具

一个基于 Model Context Protocol (MCP) 的股票分析工具，提供实时股票数据获取和技术分析功能。

## 功能特性

- 📈 实时股票数据获取
- 📊 技术指标分析（MA、MACD、KDJ、RSI、布林带）
- 🎯 支撑位和阻力位识别
- 📱 趋势分析和交易建议
- 🔧 MCP协议集成，可直接在Claude Desktop中使用

## 技术栈

- Python 3.9+
- MCP (Model Context Protocol)
- akshare (股票数据源)
- pandas (数据处理)
- numpy (数值计算)

## 项目结构

```
stock-analysis-mcp/
├── README.md
├── requirements.txt
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── server.py          # MCP服务器主文件
│   ├── stock_data.py      # 股票数据获取
│   ├── technical_analysis.py  # 技术分析算法
│   └── utils.py           # 工具函数
└── tests/
    ├── __init__.py
    └── test_stock_analysis.py
```

## 安装和使用

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行MCP服务器
```bash
python src/server.py
```

### 3. 配置Claude Desktop
在Claude Desktop的配置文件中添加MCP服务器配置。

## 支持的工具

- `get_stock_info`: 获取股票基本信息
- `get_stock_data`: 获取历史股票数据
- `analyze_stock`: 综合技术分析
- `calculate_indicators`: 计算技术指标

## 开发者

开发基于MCP协议的现代AI工具，提供专业的股票分析功能。
