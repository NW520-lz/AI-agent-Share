"""
配置文件
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # API配置
    API_TITLE: str = "股票分析系统API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "为Dify工作流提供股票数据分析服务"
    
    # 服务器配置
    HOST: str = "10.7.139.26"
    PORT: int = 8001
    DEBUG: bool = True
    
    # 认证配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API密钥配置（用于Bearer Token认证）
    VALID_API_KEYS: List[str] = ["xue1234", "test_api_key"]
    
    # 缓存配置
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_EXPIRE_SECONDS: int = 300  # 5分钟
    
    # 数据源配置
    AKSHARE_TIMEOUT: int = 30
    MAX_RETRY_ATTEMPTS: int = 3  # 增加重试次数以提高成功率
    ENABLE_REAL_DATA: bool = True   # 启用真实数据获取
    USE_MOCK_DATA: bool = True      # 真实数据获取失败时使用模拟数据作为备用
    OFFLINE_MODE: bool = False      # 完全离线模式
    
    # 技术指标配置
    MA_PERIODS: List[int] = [5, 10, 20, 60]
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    RSI_PERIOD: int = 14
    KDJ_PERIOD: int = 9
    BOLLINGER_PERIOD: int = 20
    BOLLINGER_STD: int = 2
    
    # 数据获取配置
    DEFAULT_DATA_DAYS: int = 60  # 默认获取60天数据
    MIN_DATA_DAYS: int = 14      # 最少14天数据
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/stock_analysis.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # 限流配置
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 60秒窗口
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


# 支持的市场类型
SUPPORTED_MARKETS = {
    "A": "A股",
    "HK": "港股", 
    "US": "美股",
    "ETF": "ETF基金"
}

# 股票代码格式验证规则
STOCK_CODE_PATTERNS = {
    "A": r"^[0-9]{6}$",           # A股：6位数字
    "HK": r"^[0-9]{5}$",          # 港股：5位数字
    "US": r"^[A-Z]{1,5}$",        # 美股：1-5位字母
    "ETF": r"^[0-9]{6}$"          # ETF：6位数字
}

# 错误消息
ERROR_MESSAGES = {
    "INVALID_STOCK_CODE": "股票代码格式不正确",
    "INVALID_MARKET_TYPE": "不支持的市场类型",
    "DATA_NOT_FOUND": "未找到股票数据",
    "CALCULATION_ERROR": "技术指标计算失败",
    "NETWORK_ERROR": "网络请求失败",
    "RATE_LIMIT_EXCEEDED": "请求频率超限",
    "UNAUTHORIZED": "认证失败",
    "INTERNAL_ERROR": "内部服务器错误"
}
