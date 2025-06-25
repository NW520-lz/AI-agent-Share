"""
请求数据模型
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
import re
from config import SUPPORTED_MARKETS, STOCK_CODE_PATTERNS


class StockAnalysisRequest(BaseModel):
    """股票分析请求模型"""
    stock_code: str = Field(..., description="股票代码", example="000333")
    market_type: str = Field(..., description="市场类型", example="A")
    period: Optional[int] = Field(30, description="分析周期（天数）", example=30)
    
    @validator('market_type')
    def validate_market_type(cls, v):
        if v not in SUPPORTED_MARKETS:
            raise ValueError(f"不支持的市场类型: {v}，支持的类型: {list(SUPPORTED_MARKETS.keys())}")
        return v
    
    @validator('stock_code')
    def validate_stock_code(cls, v, values):
        if 'market_type' in values:
            market_type = values['market_type']
            if market_type in STOCK_CODE_PATTERNS:
                pattern = STOCK_CODE_PATTERNS[market_type]
                if not re.match(pattern, v):
                    raise ValueError(f"{market_type}市场股票代码格式不正确: {v}")
        return v


class MarketOverviewRequest(BaseModel):
    """市场概览请求模型"""
    market_type: Optional[str] = Field("A", description="市场类型，默认为A股", example="A")
    
    @validator('market_type')
    def validate_market_type(cls, v):
        if v not in SUPPORTED_MARKETS:
            raise ValueError(f"不支持的市场类型: {v}，支持的类型: {list(SUPPORTED_MARKETS.keys())}")
        return v


class HealthCheckRequest(BaseModel):
    """健康检查请求模型"""
    pass
