# Dify工作流配置指南

## 🎯 概述

现在您可以在Dify工作流中使用我们的股票分析HTTP API服务！这个指南将详细说明如何配置工作流节点。

## 🚀 前置准备

### 1. 启动API服务器

在项目目录中运行：
```bash
cd stock-analysis-mcp
python -m uvicorn api_server:app --host 0.0.0.0 --port 8003
```

### 2. 验证服务状态

访问 `http://localhost:8003/health` 确认服务正常运行。

## 📊 API接口说明

我们提供了4个主要接口：

### 1. `/analyze-stock` - 综合股票分析 ⭐推荐
**用途**: 获取股票的完整技术分析报告
**方法**: POST
**URL**: `http://localhost:8003/analyze-stock`

**请求体**:
```json
{
  "stock_code": "600132",
  "market_type": "A",
  "period": "30"
}
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "stock_info": {
      "code": "600132",
      "name": "重庆啤酒",
      "current_price": 55.14,
      "change_percent": 1.12
    },
    "technical_summary": {
      "trend": "震荡",
      "ma5": 54.93,
      "ma10": 55.40,
      "ma20": 56.44,
      "rsi": 17.98,
      "support_levels": [55.23, 56.70],
      "resistance_levels": [59.60, 56.17]
    }
  }
}
```

### 2. `/stock-info` - 股票基本信息
**用途**: 获取股票基本信息和实时价格
**方法**: POST
**URL**: `http://localhost:8003/stock-info`

### 3. `/stock-history` - 历史数据
**用途**: 获取股票历史交易数据
**方法**: POST
**URL**: `http://localhost:8003/stock-history`

### 4. `/market-status` - 市场状态
**用途**: 获取当前市场开盘状态
**方法**: GET
**URL**: `http://localhost:8003/market-status`

## 🔧 Dify工作流配置步骤

### 步骤1: 配置开始节点

1. **添加输入变量**:
   - 变量名: `stock_code`
   - 类型: `文本`
   - 描述: `股票代码（如600132）`

### 步骤2: 配置变量聚合器（可选）

如果需要处理用户输入，可以添加变量聚合器：
- **输入变量**: `stock_code`
- **输出变量**: `processed_stock_code`

### 步骤3: 配置HTTP请求节点 ⭐核心

1. **基本设置**:
   - **方法**: `POST`
   - **URL**: `http://localhost:8003/analyze-stock`
   - **超时**: `60秒` (股票数据获取需要时间)

2. **请求头**:
   ```
   Content-Type: application/json
   ```

3. **请求体**:
   ```json
   {
     "stock_code": "{{#stock_code#}}",
     "market_type": "A",
     "period": "30"
   }
   ```

4. **变量映射**:
   - 将开始节点的 `stock_code` 变量映射到请求体中

### 步骤4: 配置条件判断节点

添加条件判断来处理API响应：

**条件1: 成功响应**
- **条件**: `{{#http_request.body.status#}} == "success"`
- **分支**: 继续处理数据

**条件2: 错误响应**
- **条件**: `{{#http_request.body.status#}} == "error"`
- **分支**: 返回错误信息

### 步骤5: 配置数据处理节点

使用**代码执行**节点来格式化分析结果：

```python
def main(http_response: dict) -> dict:
    """处理股票分析结果"""
    
    if http_response.get('status') != 'success':
        return {
            'analysis_result': f"分析失败: {http_response.get('error', '未知错误')}"
        }
    
    data = http_response.get('data', {})
    stock_info = data.get('stock_info', {})
    technical = data.get('technical_summary', {})
    
    # 格式化分析报告
    report = f"""📊 股票分析报告 - {stock_info.get('name', 'N/A')} ({stock_info.get('code', 'N/A')})

💰 当前价格: {stock_info.get('current_price', 'N/A')} 元
📈 涨跌幅: {stock_info.get('change_percent', 'N/A')}%

📊 趋势分析: {technical.get('trend', 'N/A')}

📈 移动平均线:
   MA5:  {technical.get('ma5', 'N/A')} 元
   MA10: {technical.get('ma10', 'N/A')} 元
   MA20: {technical.get('ma20', 'N/A')} 元

🎯 技术指标:
   RSI: {technical.get('rsi', 'N/A')}

🎯 关键位置:
   支撑位: {', '.join(map(str, technical.get('support_levels', [])))}
   阻力位: {', '.join(map(str, technical.get('resistance_levels', [])))}

⚠️ 以上分析仅供参考，投资有风险！"""
    
    return {
        'analysis_result': report,
        'raw_data': data
    }
```

### 步骤6: 配置输出节点

设置最终输出：
- **输出变量**: `analysis_result`
- **类型**: `文本`

## 🎨 完整工作流示例

```
[开始] → [变量聚合器] → [HTTP请求] → [条件判断] → [数据处理] → [结束]
   ↓           ↓            ↓           ↓           ↓         ↓
stock_code  处理输入    调用API    检查状态    格式化结果   输出报告
```

## 🔧 故障排除

### 问题1: HTTP请求超时
**解决方案**: 
- 增加超时时间到60-90秒
- 检查API服务器是否正常运行

### 问题2: 无法连接到API
**解决方案**:
- 确认API服务器已启动 (`http://localhost:8003/health`)
- 检查端口8003是否被占用
- 如果Dify运行在Docker中，使用 `host.docker.internal:8003`

### 问题3: 股票代码格式错误
**解决方案**:
- 确保使用6位数字格式 (如: 600132, 000001)
- 在变量聚合器中添加格式验证

## 📝 测试建议

### 测试用例1: 正常股票
```json
{
  "stock_code": "600132",
  "market_type": "A", 
  "period": "30"
}
```

### 测试用例2: 深圳股票
```json
{
  "stock_code": "000001",
  "market_type": "A",
  "period": "30"
}
```

### 测试用例3: 错误代码
```json
{
  "stock_code": "999999",
  "market_type": "A",
  "period": "30"
}
```

## 🎯 优化建议

1. **缓存机制**: 对于相同股票的重复请求，可以添加缓存逻辑
2. **批量分析**: 可以扩展API支持多只股票同时分析
3. **实时推送**: 可以添加WebSocket支持实时数据推送
4. **错误重试**: 在HTTP请求节点中配置重试机制

## 🎉 完成！

现在您的Dify工作流已经可以使用专业的股票分析功能了！

相比之前的方案，这个解决方案具有：
- ✅ 更稳定的本地API服务
- ✅ 完整的技术分析功能
- ✅ 标准化的JSON响应格式
- ✅ 详细的错误处理机制
- ✅ 灵活的参数配置
