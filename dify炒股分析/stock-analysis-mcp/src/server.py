"""
股票分析MCP服务器
"""

import asyncio
import json
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)
from pydantic import BaseModel
from loguru import logger

from .stock_data import stock_data_provider
from .technical_analysis import technical_analyzer


class StockAnalysisServer:
    """股票分析MCP服务器"""
    
    def __init__(self):
        self.server = Server("stock-analysis")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """列出可用工具"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_stock_info",
                        description="获取股票基本信息，包括当前价格、涨跌幅等",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "stock_code": {
                                    "type": "string",
                                    "description": "股票代码，如 '000001'"
                                }
                            },
                            "required": ["stock_code"]
                        }
                    ),
                    Tool(
                        name="get_stock_history",
                        description="获取股票历史数据",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "stock_code": {
                                    "type": "string",
                                    "description": "股票代码，如 '000001'"
                                },
                                "period": {
                                    "type": "string",
                                    "description": "获取天数，默认30天",
                                    "default": "30"
                                }
                            },
                            "required": ["stock_code"]
                        }
                    ),
                    Tool(
                        name="analyze_stock",
                        description="综合股票技术分析，包括趋势、技术指标、支撑阻力位等",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "stock_code": {
                                    "type": "string",
                                    "description": "股票代码，如 '000001'"
                                },
                                "period": {
                                    "type": "string",
                                    "description": "分析周期天数，默认30天",
                                    "default": "30"
                                }
                            },
                            "required": ["stock_code"]
                        }
                    ),
                    Tool(
                        name="get_market_status",
                        description="获取市场状态信息",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """调用工具"""
            try:
                if request.name == "get_stock_info":
                    return await self._get_stock_info(request.arguments)
                elif request.name == "get_stock_history":
                    return await self._get_stock_history(request.arguments)
                elif request.name == "analyze_stock":
                    return await self._analyze_stock(request.arguments)
                elif request.name == "get_market_status":
                    return await self._get_market_status(request.arguments)
                else:
                    raise ValueError(f"未知工具: {request.name}")
                    
            except Exception as e:
                logger.error(f"工具调用失败 {request.name}: {e}")
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"错误: {str(e)}"
                        )
                    ]
                )
    
    async def _get_stock_info(self, arguments: Dict[str, Any]) -> CallToolResult:
        """获取股票基本信息"""
        stock_code = arguments.get("stock_code")
        if not stock_code:
            raise ValueError("缺少股票代码参数")
        
        # 获取股票信息
        stock_info = stock_data_provider.get_stock_info(stock_code)
        
        # 格式化输出
        result_text = f"""📈 股票信息 - {stock_info['name']} ({stock_info['code']})

💰 当前价格: {stock_info['current_price']:.2f} 元
📊 涨跌额: {stock_info['change']:.2f} 元
📈 涨跌幅: {stock_info['change_percent']:.2f}%
🏢 市场: {stock_info['market']}股

"""
        
        if 'error' in stock_info:
            result_text += f"⚠️ 注意: {stock_info['error']}"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                )
            ]
        )
    
    async def _get_stock_history(self, arguments: Dict[str, Any]) -> CallToolResult:
        """获取股票历史数据"""
        stock_code = arguments.get("stock_code")
        period = arguments.get("period", "30")
        
        if not stock_code:
            raise ValueError("缺少股票代码参数")
        
        # 获取历史数据
        df = stock_data_provider.get_stock_history(stock_code, period)
        
        if df.empty:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ 无法获取股票 {stock_code} 的历史数据"
                    )
                ]
            )
        
        # 格式化输出最近几天的数据
        recent_data = df.tail(5)
        result_text = f"""📊 股票历史数据 - {stock_code} (最近5天)

"""
        
        for _, row in recent_data.iterrows():
            result_text += f"""📅 {row['date']}
   开盘: {row['open']:.2f}  收盘: {row['close']:.2f}
   最高: {row['high']:.2f}  最低: {row['low']:.2f}
   成交量: {row['volume']:,.0f}

"""
        
        result_text += f"📈 总共获取 {len(df)} 天的数据"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                )
            ]
        )
    
    async def _analyze_stock(self, arguments: Dict[str, Any]) -> CallToolResult:
        """综合股票分析"""
        stock_code = arguments.get("stock_code")
        period = arguments.get("period", "30")
        
        if not stock_code:
            raise ValueError("缺少股票代码参数")
        
        # 获取股票基本信息
        stock_info = stock_data_provider.get_stock_info(stock_code)
        
        # 获取历史数据
        df = stock_data_provider.get_stock_history(stock_code, period)
        
        if df.empty:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ 无法获取股票 {stock_code} 的历史数据，无法进行技术分析"
                    )
                ]
            )
        
        # 进行技术分析
        analysis = technical_analyzer.comprehensive_analysis(df)
        
        if 'error' in analysis:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"❌ 技术分析失败: {analysis['error']}"
                    )
                ]
            )
        
        # 格式化分析结果
        result_text = f"""🔍 股票技术分析报告 - {stock_info['name']} ({stock_code})

💰 当前价格: {stock_info['current_price']:.2f} 元
📈 涨跌幅: {stock_info['change_percent']:.2f}%

📊 趋势分析: {analysis['trend']}

📈 移动平均线:
   MA5:  {analysis['ma5']:.2f} 元
   MA10: {analysis['ma10']:.2f} 元  
   MA20: {analysis['ma20']:.2f} 元
   MA60: {analysis['ma60']:.2f} 元 (如有)

🎯 技术指标:
   MACD: {analysis['macd']:.4f}
   信号线: {analysis['macd_signal']:.4f}
   柱状图: {analysis['macd_histogram']:.4f}
   
   RSI: {analysis['rsi']:.2f}
   
   KDJ:
   K: {analysis['kdj_k']:.2f}
   D: {analysis['kdj_d']:.2f}  
   J: {analysis['kdj_j']:.2f}

📊 布林带:
   上轨: {analysis['bollinger_upper']:.2f}
   中轨: {analysis['bollinger_middle']:.2f}
   下轨: {analysis['bollinger_lower']:.2f}

🎯 关键位置:
   支撑位: {', '.join([f'{level:.2f}' for level in analysis['support_levels']])}
   阻力位: {', '.join([f'{level:.2f}' for level in analysis['resistance_levels']])}

📝 分析基于最近 {period} 天的数据
"""
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                )
            ]
        )
    
    async def _get_market_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """获取市场状态"""
        market_status = stock_data_provider.get_market_status()
        
        status_emoji = "🟢" if market_status['market_status'] == 'open' else "🔴"
        
        result_text = f"""🏢 A股市场状态

{status_emoji} 市场状态: {market_status['market_status']}
🕐 当前时间: {market_status['current_time']}
📅 是否交易日: {'是' if market_status['is_trading_day'] else '否'}
⏰ 是否交易时间: {'是' if market_status['is_trading_time'] else '否'}

📋 交易时间:
   上午: 09:30 - 11:30
   下午: 13:00 - 15:00
"""
        
        if 'error' in market_status:
            result_text += f"\n⚠️ 注意: {market_status['error']}"
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=result_text
                )
            ]
        )
    
    async def run(self):
        """运行服务器"""
        logger.info("启动股票分析MCP服务器...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="stock-analysis",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


async def main():
    """主函数"""
    server = StockAnalysisServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
