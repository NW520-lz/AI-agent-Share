"""
响应数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class StockInfo(BaseModel):
    """股票基础信息"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    market: str = Field(..., description="市场类型")
    current_price: Optional[float] = Field(None, description="当前价格")
    change: Optional[float] = Field(None, description="涨跌额")
    change_percent: Optional[float] = Field(None, description="涨跌幅")


class TechnicalSummary(BaseModel):
    """技术指标摘要"""
    trend: str = Field(..., description="趋势判断")
    ma5: Optional[float] = Field(None, description="5日均线")
    ma10: Optional[float] = Field(None, description="10日均线")
    ma20: Optional[float] = Field(None, description="20日均线")
    ma60: Optional[float] = Field(None, description="60日均线")
    macd: Optional[float] = Field(None, description="MACD值")
    macd_signal: Optional[float] = Field(None, description="MACD信号线")
    macd_histogram: Optional[float] = Field(None, description="MACD柱状图")
    kdj_k: Optional[float] = Field(None, description="KDJ K值")
    kdj_d: Optional[float] = Field(None, description="KDJ D值")
    kdj_j: Optional[float] = Field(None, description="KDJ J值")
    rsi: Optional[float] = Field(None, description="RSI指标")
    bollinger_upper: Optional[float] = Field(None, description="布林带上轨")
    bollinger_middle: Optional[float] = Field(None, description="布林带中轨")
    bollinger_lower: Optional[float] = Field(None, description="布林带下轨")
    support_levels: List[float] = Field(default_factory=list, description="支撑位")
    resistance_levels: List[float] = Field(default_factory=list, description="阻力位")


class RecentData(BaseModel):
    """历史交易数据"""
    date: str = Field(..., description="交易日期")
    open: float = Field(..., description="开盘价")
    close: float = Field(..., description="收盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    volume: int = Field(..., description="成交量")
    amount: Optional[float] = Field(None, description="成交额")


class AnalysisReport(BaseModel):
    """分析报告"""
    trend_analysis: str = Field(..., description="趋势分析")
    volume_analysis: str = Field(..., description="成交量分析")
    risk_assessment: str = Field(..., description="风险评估")
    support_resistance: str = Field(..., description="支撑阻力分析")
    trading_suggestion: str = Field(..., description="交易建议")


class StockAnalysisResponse(BaseModel):
    """股票分析响应模型"""
    status: str = Field(..., description="响应状态")
    data: Dict[str, Any] = Field(..., description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class MarketIndex(BaseModel):
    """市场指数信息"""
    name: str = Field(..., description="指数名称")
    code: str = Field(..., description="指数代码")
    current_value: float = Field(..., description="当前点位")
    change: float = Field(..., description="涨跌点数")
    change_percent: float = Field(..., description="涨跌幅")


class SectorInfo(BaseModel):
    """行业板块信息"""
    name: str = Field(..., description="板块名称")
    change_percent: float = Field(..., description="涨跌幅")
    leading_stocks: List[str] = Field(default_factory=list, description="龙头股票")


class MarketOverviewResponse(BaseModel):
    """市场概览响应模型"""
    status: str = Field(..., description="响应状态")
    data: Dict[str, Any] = Field(..., description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    status: str = Field("error", description="响应状态")
    error_code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field("healthy", description="服务状态")
    version: str = Field(..., description="服务版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="依赖服务状态")
