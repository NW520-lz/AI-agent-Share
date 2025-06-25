"""
股票分析HTTP API服务器
为Dify工作流提供HTTP接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.stock_data import stock_data_provider
from src.technical_analysis import technical_analyzer
from src.utils import validate_stock_code, normalize_stock_code

# 创建FastAPI应用
app = FastAPI(
    title="股票分析API",
    description="为Dify工作流提供股票数据获取和技术分析功能",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class StockAnalysisRequest(BaseModel):
    stock_code: str
    market_type: str = "A"
    period: Optional[str] = "30"

class StockInfoRequest(BaseModel):
    stock_code: str
    market_type: str = "A"

class StockHistoryRequest(BaseModel):
    stock_code: str
    period: Optional[str] = "30"
    market_type: str = "A"

# 响应模型
class APIResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "股票分析API服务",
        "version": "1.0.0",
        "endpoints": [
            "/stock-info",
            "/stock-history", 
            "/analyze-stock",
            "/market-status"
        ]
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "stock-analysis-api"}

@app.post("/stock-info")
async def get_stock_info(request: StockInfoRequest):
    """
    获取股票基本信息
    """
    try:
        # 验证股票代码
        stock_code = normalize_stock_code(request.stock_code)
        if not validate_stock_code(stock_code):
            raise HTTPException(status_code=400, detail="无效的股票代码格式")
        
        # 获取股票信息
        stock_info = stock_data_provider.get_stock_info(stock_code)
        
        return APIResponse(
            status="success",
            data={
                "stock_info": stock_info
            }
        )
        
    except Exception as e:
        return APIResponse(
            status="error",
            error=str(e)
        )

@app.post("/stock-history")
async def get_stock_history(request: StockHistoryRequest):
    """
    获取股票历史数据
    """
    try:
        # 验证股票代码
        stock_code = normalize_stock_code(request.stock_code)
        if not validate_stock_code(stock_code):
            raise HTTPException(status_code=400, detail="无效的股票代码格式")
        
        # 获取历史数据
        df = stock_data_provider.get_stock_history(stock_code, request.period)
        
        if df.empty:
            return APIResponse(
                status="error",
                error="无法获取历史数据"
            )
        
        # 转换为字典格式
        history_data = []
        for _, row in df.iterrows():
            history_data.append({
                "date": str(row['date']),
                "open": float(row['open']) if row['open'] is not None else None,
                "close": float(row['close']) if row['close'] is not None else None,
                "high": float(row['high']) if row['high'] is not None else None,
                "low": float(row['low']) if row['low'] is not None else None,
                "volume": int(row['volume']) if row['volume'] is not None else None,
                "amount": float(row['amount']) if 'amount' in row and row['amount'] is not None else None
            })
        
        return APIResponse(
            status="success",
            data={
                "stock_code": stock_code,
                "period": request.period,
                "total_records": len(history_data),
                "history_data": history_data
            }
        )
        
    except Exception as e:
        return APIResponse(
            status="error",
            error=str(e)
        )

@app.post("/analyze-stock")
async def analyze_stock(request: StockAnalysisRequest):
    """
    综合股票技术分析
    """
    try:
        # 验证股票代码
        stock_code = normalize_stock_code(request.stock_code)
        if not validate_stock_code(stock_code):
            raise HTTPException(status_code=400, detail="无效的股票代码格式")
        
        # 获取股票基本信息
        stock_info = stock_data_provider.get_stock_info(stock_code)
        
        # 获取历史数据
        df = stock_data_provider.get_stock_history(stock_code, request.period)
        
        if df.empty:
            return APIResponse(
                status="error",
                error="无法获取历史数据，无法进行技术分析"
            )
        
        # 进行技术分析
        analysis = technical_analyzer.comprehensive_analysis(df)
        
        if 'error' in analysis:
            return APIResponse(
                status="error",
                error=f"技术分析失败: {analysis['error']}"
            )
        
        # 格式化分析结果
        technical_summary = {
            "trend": analysis['trend'],
            "ma5": float(analysis['ma5']) if analysis['ma5'] is not None else None,
            "ma10": float(analysis['ma10']) if analysis['ma10'] is not None else None,
            "ma20": float(analysis['ma20']) if analysis['ma20'] is not None else None,
            "ma60": float(analysis['ma60']) if analysis['ma60'] is not None else None,
            "macd": float(analysis['macd']) if analysis['macd'] is not None else None,
            "macd_signal": float(analysis['macd_signal']) if analysis['macd_signal'] is not None else None,
            "macd_histogram": float(analysis['macd_histogram']) if analysis['macd_histogram'] is not None else None,
            "kdj_k": float(analysis['kdj_k']) if analysis['kdj_k'] is not None else None,
            "kdj_d": float(analysis['kdj_d']) if analysis['kdj_d'] is not None else None,
            "kdj_j": float(analysis['kdj_j']) if analysis['kdj_j'] is not None else None,
            "rsi": float(analysis['rsi']) if analysis['rsi'] is not None else None,
            "bollinger_upper": float(analysis['bollinger_upper']) if analysis['bollinger_upper'] is not None else None,
            "bollinger_middle": float(analysis['bollinger_middle']) if analysis['bollinger_middle'] is not None else None,
            "bollinger_lower": float(analysis['bollinger_lower']) if analysis['bollinger_lower'] is not None else None,
            "support_levels": [float(level) for level in analysis['support_levels']],
            "resistance_levels": [float(level) for level in analysis['resistance_levels']]
        }
        
        # 获取最近几天的数据
        recent_data = []
        for _, row in df.tail(5).iterrows():
            recent_data.append({
                "date": str(row['date']),
                "open": float(row['open']) if row['open'] is not None else None,
                "close": float(row['close']) if row['close'] is not None else None,
                "high": float(row['high']) if row['high'] is not None else None,
                "low": float(row['low']) if row['low'] is not None else None,
                "volume": int(row['volume']) if row['volume'] is not None else None,
                "amount": float(row['amount']) if 'amount' in row and row['amount'] is not None else None
            })
        
        return APIResponse(
            status="success",
            data={
                "stock_info": {
                    "code": stock_info['code'],
                    "name": stock_info['name'],
                    "market": stock_info['market'],
                    "current_price": float(stock_info['current_price']) if stock_info['current_price'] is not None else None,
                    "change": float(stock_info['change']) if stock_info['change'] is not None else None,
                    "change_percent": float(stock_info['change_percent']) if stock_info['change_percent'] is not None else None
                },
                "technical_summary": technical_summary,
                "recent_data": recent_data,
                "analysis_period": request.period,
                "total_data_points": len(df)
            }
        )
        
    except Exception as e:
        return APIResponse(
            status="error",
            error=str(e)
        )

@app.get("/market-status")
async def get_market_status():
    """
    获取市场状态
    """
    try:
        market_status = stock_data_provider.get_market_status()
        
        return APIResponse(
            status="success",
            data={
                "market_status": market_status
            }
        )
        
    except Exception as e:
        return APIResponse(
            status="error",
            error=str(e)
        )

if __name__ == "__main__":
    print("🚀 启动股票分析HTTP API服务器...")
    print("📡 API文档地址: http://localhost:8003/docs")
    print("🔧 为Dify工作流提供股票分析功能")
    print("=" * 50)

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )
