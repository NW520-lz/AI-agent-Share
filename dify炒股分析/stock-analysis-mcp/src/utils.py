"""
工具函数模块
"""

import re
from typing import Optional, Tuple
from datetime import datetime, timedelta


def validate_stock_code(stock_code: str) -> bool:
    """
    验证股票代码格式
    
    Args:
        stock_code: 股票代码
        
    Returns:
        是否为有效的股票代码
    """
    if not stock_code:
        return False
    
    # A股代码格式：6位数字
    pattern = r'^\d{6}$'
    return bool(re.match(pattern, stock_code))


def normalize_stock_code(stock_code: str) -> str:
    """
    标准化股票代码
    
    Args:
        stock_code: 原始股票代码
        
    Returns:
        标准化后的股票代码
    """
    if not stock_code:
        return ""
    
    # 移除空格和特殊字符
    code = re.sub(r'[^\d]', '', stock_code)
    
    # 确保是6位数字
    if len(code) == 6:
        return code
    elif len(code) < 6:
        # 左侧补零
        return code.zfill(6)
    else:
        # 取前6位
        return code[:6]


def get_market_from_code(stock_code: str) -> str:
    """
    根据股票代码判断市场
    
    Args:
        stock_code: 股票代码
        
    Returns:
        市场类型
    """
    if not stock_code or len(stock_code) != 6:
        return "未知"
    
    first_digit = stock_code[0]
    
    if first_digit in ['0', '3']:
        return "深圳"
    elif first_digit == '6':
        return "上海"
    elif first_digit == '8':
        return "北京"
    else:
        return "其他"


def format_number(number: Optional[float], decimal_places: int = 2) -> str:
    """
    格式化数字显示
    
    Args:
        number: 要格式化的数字
        decimal_places: 小数位数
        
    Returns:
        格式化后的字符串
    """
    if number is None:
        return "N/A"
    
    try:
        return f"{number:.{decimal_places}f}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(number: Optional[float], decimal_places: int = 2) -> str:
    """
    格式化百分比显示
    
    Args:
        number: 要格式化的数字
        decimal_places: 小数位数
        
    Returns:
        格式化后的百分比字符串
    """
    if number is None:
        return "N/A"
    
    try:
        return f"{number:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_volume(volume: Optional[float]) -> str:
    """
    格式化成交量显示
    
    Args:
        volume: 成交量
        
    Returns:
        格式化后的成交量字符串
    """
    if volume is None:
        return "N/A"
    
    try:
        if volume >= 100000000:  # 亿
            return f"{volume/100000000:.2f}亿"
        elif volume >= 10000:  # 万
            return f"{volume/10000:.2f}万"
        else:
            return f"{volume:.0f}"
    except (ValueError, TypeError):
        return "N/A"


def get_trading_days(start_date: datetime, end_date: datetime) -> int:
    """
    计算交易日天数（简单计算，不考虑节假日）
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        交易日天数
    """
    total_days = (end_date - start_date).days
    weeks = total_days // 7
    remaining_days = total_days % 7
    
    # 计算剩余天数中的工作日
    weekday_start = start_date.weekday()
    trading_days_in_remaining = 0
    
    for i in range(remaining_days):
        day_of_week = (weekday_start + i) % 7
        if day_of_week < 5:  # 周一到周五
            trading_days_in_remaining += 1
    
    return weeks * 5 + trading_days_in_remaining


def calculate_change_percentage(current: float, previous: float) -> float:
    """
    计算涨跌幅
    
    Args:
        current: 当前价格
        previous: 前一价格
        
    Returns:
        涨跌幅百分比
    """
    if previous == 0:
        return 0.0
    
    return ((current - previous) / previous) * 100


def get_trend_emoji(trend: str) -> str:
    """
    根据趋势获取对应的emoji
    
    Args:
        trend: 趋势描述
        
    Returns:
        对应的emoji
    """
    trend_lower = trend.lower()
    
    if "上升" in trend_lower or "上涨" in trend_lower:
        return "📈"
    elif "下降" in trend_lower or "下跌" in trend_lower:
        return "📉"
    elif "震荡" in trend_lower or "横盘" in trend_lower:
        return "📊"
    else:
        return "❓"


def get_rsi_signal(rsi: float) -> Tuple[str, str]:
    """
    根据RSI值获取信号
    
    Args:
        rsi: RSI值
        
    Returns:
        信号描述和emoji
    """
    if rsi >= 80:
        return "超买", "🔴"
    elif rsi >= 70:
        return "偏高", "🟡"
    elif rsi <= 20:
        return "超卖", "🟢"
    elif rsi <= 30:
        return "偏低", "🟡"
    else:
        return "正常", "⚪"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 默认值
        
    Returns:
        除法结果或默认值
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default
