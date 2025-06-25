# 股票分析系统API服务

基于FastAPI和AKShare的股票分析系统，为Dify工作流提供专业的股票数据分析服务。

## 功能特性

- 🚀 **多市场支持**: 支持A股、港股、美股、ETF等多种市场
- 📊 **技术指标**: 计算MA、MACD、KDJ、RSI、布林带等常用技术指标
- 📈 **智能分析**: 生成趋势分析、成交量分析、风险评估等专业报告
- 🔐 **安全认证**: Bearer Token认证机制，确保API安全访问
- ⚡ **高性能**: 内置缓存机制，优化响应速度
- 🔧 **易集成**: RESTful API设计，方便与Dify等平台集成

## 快速开始

### 环境要求

- Python 3.8+
- pip 或 conda

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

创建 `.env` 文件（可选）：

```env
# API配置
API_TITLE=股票分析系统API
DEBUG=False

# 认证配置
VALID_API_KEYS=["xue1234", "your_api_key"]

# 缓存配置
CACHE_EXPIRE_SECONDS=300

# 日志配置
LOG_LEVEL=INFO
```

### 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

### API文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API接口

### 1. 股票分析接口

**接口地址**: `POST /analyze-stock/`

**请求头**:
```
Authorization: bearer xue1234
Content-Type: application/json
```

**请求参数**:
```json
{
  "stock_code": "000333",
  "market_type": "A"
}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "stock_info": {
      "code": "000333",
      "name": "美的集团",
      "market": "A",
      "current_price": 57.8,
      "change": 1.2,
      "change_percent": 2.12
    },
    "technical_summary": {
      "trend": "上升",
      "ma5": 56.78,
      "ma10": 55.43,
      "ma20": 53.21,
      "macd": 1.25,
      "kdj_k": 75.6,
      "kdj_d": 68.3,
      "kdj_j": 82.9,
      "rsi": 65.7,
      "support_levels": [54.2, 52.8],
      "resistance_levels": [58.5, 60.2]
    },
    "recent_data": [...],
    "report": {
      "trend_analysis": "股票呈现上升趋势...",
      "volume_analysis": "成交量温和放大...",
      "risk_assessment": "短期RSI达到65.7...",
      "support_resistance": "近期支撑位在54.2元...",
      "trading_suggestion": "可考虑在回调至支撑位附近买入..."
    }
  },
  "timestamp": "2023-05-24T10:30:00"
}
```

### 2. 市场概览接口

**接口地址**: `GET /market-overview/?market_type=A`

**请求头**:
```
Authorization: bearer xue1234
```

### 3. 健康检查接口

**接口地址**: `GET /health`

## 支持的市场类型

| 市场类型 | 说明 | 股票代码格式 |
|---------|------|-------------|
| A | A股市场 | 6位数字 (如: 000001) |
| HK | 港股市场 | 5位数字 (如: 00700) |
| US | 美股市场 | 1-5位字母 (如: AAPL) |
| ETF | ETF基金 | 6位数字 (如: 510300) |

## 技术指标说明

### 移动平均线 (MA)
- MA5: 5日移动平均线
- MA10: 10日移动平均线  
- MA20: 20日移动平均线
- MA60: 60日移动平均线

### MACD指标
- MACD: 差离值
- MACD Signal: 信号线
- MACD Histogram: 柱状图

### KDJ指标
- K值: 快速随机指标
- D值: 慢速随机指标
- J值: 超前指标

### 其他指标
- RSI: 相对强弱指标
- 布林带: 上轨、中轨、下轨
- 支撑阻力位: 技术分析关键位置

## 与Dify集成

在Dify工作流中添加HTTP请求节点：

1. **请求方式**: POST
2. **URL**: `http://your-server:8000/analyze-stock/`
3. **请求头**: 
   ```
   Authorization: bearer xue1234
   Content-Type: application/json
   ```
4. **请求体**: 
   ```json
   {
     "stock_code": "{{stock_code}}",
     "market_type": "{{market_type}}"
   }
   ```

## 错误处理

API使用标准HTTP状态码：

- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 认证失败
- `404`: 数据未找到
- `500`: 服务器内部错误

错误响应格式：
```json
{
  "status": "error",
  "error_code": "INVALID_STOCK_CODE",
  "message": "股票代码格式不正确",
  "timestamp": "2023-05-24T10:30:00"
}
```

## 开发说明

### 项目结构

```
├── main.py                 # FastAPI应用入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖包
├── models/                # 数据模型
│   ├── request_models.py  # 请求模型
│   └── response_models.py # 响应模型
├── services/              # 业务逻辑
│   ├── stock_data_service.py    # 股票数据获取
│   ├── technical_analysis.py   # 技术指标计算
│   └── report_generator.py     # 报告生成
└── utils/                 # 工具函数
    ├── auth.py           # 认证相关
    └── cache.py          # 缓存相关
```

### 扩展开发

1. **添加新的技术指标**: 在 `services/technical_analysis.py` 中添加计算方法
2. **支持新的市场**: 在 `services/stock_data_service.py` 中添加数据获取逻辑
3. **自定义分析报告**: 修改 `services/report_generator.py` 中的报告生成逻辑

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
# AI-agent-Share
