"""
股票分析系统API服务
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
from typing import Dict, Any

# 导入配置和模型
from config import settings, ERROR_MESSAGES
from models.request_models import StockAnalysisRequest, MarketOverviewRequest
from models.response_models import (
    StockAnalysisResponse, MarketOverviewResponse, 
    ErrorResponse, HealthCheckResponse
)

# 导入服务
from services.stock_data_service import stock_data_service
from services.technical_analysis import technical_analysis
from services.report_generator import report_generator

# 导入认证
from utils.auth import get_current_api_key

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message=ERROR_MESSAGES["INTERNAL_ERROR"]
        ).dict()
    )


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """根路径健康检查"""
    return HealthCheckResponse(
        version=settings.API_VERSION,
        dependencies={
            "akshare": "正常",
            "talib": "正常"
        }
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """健康检查接口"""
    return HealthCheckResponse(
        version=settings.API_VERSION,
        dependencies={
            "akshare": "正常",
            "talib": "正常"
        }
    )


@app.post("/analyze-stock/", response_model=StockAnalysisResponse)
async def analyze_stock(
    request: StockAnalysisRequest,
    api_key: str = Depends(get_current_api_key)
):
    """
    股票分析接口

    根据股票代码和市场类型获取股票数据，计算技术指标，生成分析报告
    """
    try:
        logger.info(f"开始分析股票: {request.stock_code}, 市场: {request.market_type}")
        
        # 1. 获取股票数据
        stock_data = await stock_data_service.get_stock_data(
            request.stock_code,
            request.market_type,
            request.period
        )
        
        if not stock_data or not stock_data.get('recent_data'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES["DATA_NOT_FOUND"]
            )
        
        # 2. 计算技术指标
        raw_data = stock_data.get('raw_data')
        if raw_data is not None and not raw_data.empty:
            technical_indicators = technical_analysis.calculate_all_indicators(raw_data)
        else:
            technical_indicators = technical_analysis._get_empty_indicators()
        
        # 3. 生成分析报告
        analysis_report = report_generator.generate_analysis_report(
            stock_data['stock_info'],
            technical_indicators,
            stock_data['recent_data']
        )
        
        # 4. 构建响应数据
        response_data = {
            "stock_info": stock_data['stock_info'],
            "technical_summary": {
                "trend": technical_indicators.get('trend', '未知'),
                "ma5": technical_indicators.get('ma5'),
                "ma10": technical_indicators.get('ma10'),
                "ma20": technical_indicators.get('ma20'),
                "ma60": technical_indicators.get('ma60'),
                "macd": technical_indicators.get('macd'),
                "macd_signal": technical_indicators.get('macd_signal'),
                "macd_histogram": technical_indicators.get('macd_histogram'),
                "kdj_k": technical_indicators.get('kdj_k'),
                "kdj_d": technical_indicators.get('kdj_d'),
                "kdj_j": technical_indicators.get('kdj_j'),
                "rsi": technical_indicators.get('rsi'),
                "bollinger_upper": technical_indicators.get('bollinger_upper'),
                "bollinger_middle": technical_indicators.get('bollinger_middle'),
                "bollinger_lower": technical_indicators.get('bollinger_lower'),
                "support_levels": technical_indicators.get('support_levels', []),
                "resistance_levels": technical_indicators.get('resistance_levels', [])
            },
            "recent_data": stock_data['recent_data'][-14:],  # 返回最近14天数据
            "report": analysis_report
        }
        
        logger.info(f"股票分析完成: {request.stock_code}")
        
        return StockAnalysisResponse(
            status="success",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"股票分析失败: {request.stock_code}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@app.post("/analyze-stock-test/", response_model=StockAnalysisResponse)
async def analyze_stock_test(request: StockAnalysisRequest):
    """
    股票分析测试接口（无需认证）

    用于测试Dify连接，不需要API密钥认证
    """
    try:
        logger.info(f"开始分析股票（测试模式）: {request.stock_code}, 市场: {request.market_type}")

        # 1. 获取股票数据
        stock_data = await stock_data_service.get_stock_data(
            request.stock_code,
            request.market_type,
            request.period
        )

        if not stock_data or not stock_data.get('recent_data'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGES["DATA_NOT_FOUND"]
            )

        # 2. 计算技术指标
        raw_data = stock_data.get('raw_data')
        if raw_data is not None and not raw_data.empty:
            technical_indicators = technical_analysis.calculate_all_indicators(raw_data)
        else:
            technical_indicators = technical_analysis._get_empty_indicators()

        # 3. 生成分析报告
        analysis_report = report_generator.generate_analysis_report(
            stock_data['stock_info'],
            technical_indicators,
            stock_data['recent_data']
        )

        # 4. 构建响应数据
        response_data = {
            "stock_info": stock_data['stock_info'],
            "technical_summary": {
                "trend": technical_indicators.get('trend', '未知'),
                "ma5": technical_indicators.get('ma5'),
                "ma10": technical_indicators.get('ma10'),
                "ma20": technical_indicators.get('ma20'),
                "ma60": technical_indicators.get('ma60'),
                "macd": technical_indicators.get('macd'),
                "macd_signal": technical_indicators.get('macd_signal'),
                "macd_histogram": technical_indicators.get('macd_histogram'),
                "kdj_k": technical_indicators.get('kdj_k'),
                "kdj_d": technical_indicators.get('kdj_d'),
                "kdj_j": technical_indicators.get('kdj_j'),
                "rsi": technical_indicators.get('rsi'),
                "bollinger_upper": technical_indicators.get('bollinger_upper'),
                "bollinger_middle": technical_indicators.get('bollinger_middle'),
                "bollinger_lower": technical_indicators.get('bollinger_lower'),
                "support_levels": technical_indicators.get('support_levels', []),
                "resistance_levels": technical_indicators.get('resistance_levels', [])
            },
            "recent_data": stock_data['recent_data'][-14:],  # 返回最近14天数据
            "report": analysis_report
        }

        logger.info(f"股票分析完成（测试模式）: {request.stock_code}")

        return StockAnalysisResponse(
            status="success",
            data=response_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"股票分析失败（测试模式）: {request.stock_code}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析失败: {str(e)}"
        )


@app.get("/market-overview/", response_model=MarketOverviewResponse)
async def market_overview(
    market_type: str = "A",
    api_key: str = Depends(get_current_api_key)
):
    """
    市场概览接口
    
    获取指定市场的整体概况数据
    """
    try:
        logger.info(f"获取市场概览: {market_type}")
        
        # 这里可以实现市场概览的具体逻辑
        # 暂时返回示例数据
        market_data = {
            "market_info": {
                "market_type": market_type,
                "market_name": "A股市场" if market_type == "A" else f"{market_type}市场",
                "trading_status": "正常交易"
            },
            "main_indices": [
                {
                    "name": "上证指数",
                    "code": "000001",
                    "current_value": 3200.0,
                    "change": 15.6,
                    "change_percent": 0.49
                }
            ],
            "sector_performance": [
                {
                    "name": "科技股",
                    "change_percent": 2.1,
                    "leading_stocks": ["000001", "000002"]
                }
            ]
        }
        
        logger.info(f"市场概览获取完成: {market_type}")
        
        return MarketOverviewResponse(
            status="success",
            data=market_data
        )
        
    except Exception as e:
        logger.error(f"获取市场概览失败: {market_type}, 错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取市场概览失败: {str(e)}"
        )


if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
