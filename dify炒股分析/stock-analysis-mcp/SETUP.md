# 股票分析MCP工具配置指南

## 📋 前置要求

1. **Python 3.9+** 已安装
2. **Claude Desktop** 已安装
3. **网络连接** 用于获取股票数据

## 🚀 安装步骤

### 1. 安装依赖包

```bash
cd stock-analysis-mcp
pip install -r requirements.txt
```

### 2. 测试基础功能

```bash
python test_basic.py
```

如果看到类似以下输出，说明基础功能正常：
```
✅ 基础功能测试完成！
```

### 3. 配置Claude Desktop

#### 方法一：自动配置（推荐）

1. 找到Claude Desktop配置文件位置：
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. 复制我们提供的配置内容到该文件：

```json
{
  "mcpServers": {
    "stock-analysis": {
      "command": "python",
      "args": [
        "d:/AI agent/dify智能体/作品应用/dify炒股分析/stock-analysis-mcp/src/server.py"
      ],
      "env": {
        "PYTHONPATH": "d:/AI agent/dify智能体/作品应用/dify炒股分析/stock-analysis-mcp/src"
      }
    }
  }
}
```

**⚠️ 重要：请将路径修改为您的实际项目路径！**

#### 方法二：手动配置

1. 打开Claude Desktop
2. 进入设置 → MCP服务器
3. 添加新的MCP服务器：
   - **名称**: `stock-analysis`
   - **命令**: `python`
   - **参数**: `[您的项目路径]/src/server.py`

### 4. 重启Claude Desktop

配置完成后，重启Claude Desktop以加载MCP服务器。

### 5. 验证配置

在Claude Desktop中输入以下测试命令：

```
请帮我获取股票000001的基本信息
```

如果配置成功，您应该看到股票分析工具的响应。

## 🛠️ 可用工具

配置成功后，您可以使用以下工具：

### 1. 获取股票基本信息
```
获取股票000001的基本信息
```

### 2. 获取股票历史数据
```
获取股票000001最近30天的历史数据
```

### 3. 综合技术分析
```
分析股票000001的技术指标
```

### 4. 获取市场状态
```
查看当前市场状态
```

## 🔧 故障排除

### 问题1：MCP服务器无法启动

**解决方案：**
1. 检查Python路径是否正确
2. 确认所有依赖包已安装
3. 检查项目路径是否正确

### 问题2：无法获取股票数据

**解决方案：**
1. 检查网络连接
2. 确认股票代码格式正确（6位数字）
3. 某些数据源可能有访问限制，稍后重试

### 问题3：Claude Desktop无法识别工具

**解决方案：**
1. 确认配置文件路径正确
2. 检查JSON格式是否正确
3. 重启Claude Desktop
4. 查看Claude Desktop的错误日志

## 📊 支持的股票代码格式

- **A股代码**: 6位数字，如 `000001`、`600000`、`300001`
- **市场识别**:
  - `000xxx`、`300xxx`: 深圳市场
  - `600xxx`: 上海市场
  - `800xxx`: 北京市场

## 🎯 技术指标说明

我们的工具支持以下技术指标：

- **移动平均线**: MA5, MA10, MA20, MA60
- **MACD**: 快线、慢线、柱状图
- **RSI**: 相对强弱指标
- **KDJ**: 随机指标
- **布林带**: 上轨、中轨、下轨
- **支撑阻力位**: 自动识别关键价位

## 📈 使用示例

### 基础查询
```
帮我查看平安银行(000001)的当前股价
```

### 技术分析
```
分析比亚迪(002594)的技术指标，包括MACD和RSI
```

### 趋势分析
```
分析茅台(600519)最近30天的价格趋势
```

## 🔄 更新和维护

### 更新依赖包
```bash
pip install -r requirements.txt --upgrade
```

### 查看日志
MCP服务器的日志会显示在Claude Desktop的控制台中。

## 📞 技术支持

如果遇到问题，请检查：
1. Python版本是否兼容
2. 依赖包是否正确安装
3. 配置文件路径是否正确
4. 网络连接是否正常

---

🎉 **恭喜！您已成功配置股票分析MCP工具！**

现在您可以在Claude Desktop中直接使用专业的股票分析功能了！
