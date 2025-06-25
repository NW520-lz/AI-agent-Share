"""
股票数据获取模块
支持从多个数据源获取股票数据
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger
import time


class StockDataProvider:
    """股票数据提供者"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5分钟缓存
        
    def _get_cache_key(self, stock_code: str, data_type: str) -> str:
        """生成缓存键"""
        return f"{stock_code}_{data_type}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key].get('timestamp', 0)
        return time.time() - cache_time < self.cache_timeout
    
    def get_stock_info(self, stock_code: str) -> Dict:
        """
        获取股票基本信息
        
        Args:
            stock_code: 股票代码，如 '000001'
            
        Returns:
            股票基本信息字典
        """
        cache_key = self._get_cache_key(stock_code, 'info')
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # 获取股票基本信息
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            
            # 获取实时价格
            realtime_data = ak.stock_zh_a_spot_em()
            stock_realtime = realtime_data[realtime_data['代码'] == stock_code]
            
            if not stock_realtime.empty:
                current_price = float(stock_realtime.iloc[0]['最新价'])
                change = float(stock_realtime.iloc[0]['涨跌额'])
                change_percent = float(stock_realtime.iloc[0]['涨跌幅'])
                name = stock_realtime.iloc[0]['名称']
            else:
                current_price = None
                change = None
                change_percent = None
                name = f"股票{stock_code}"
            
            result = {
                'code': stock_code,
                'name': name,
                'market': 'A',  # A股
                'current_price': current_price,
                'change': change,
                'change_percent': change_percent,
                'info': stock_info.to_dict() if not stock_info.empty else {}
            }
            
            # 缓存结果
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            
            logger.info(f"获取股票 {stock_code} 基本信息成功")
            return result
            
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 基本信息失败: {e}")
            return {
                'code': stock_code,
                'name': f"股票{stock_code}",
                'market': 'A',
                'current_price': None,
                'change': None,
                'change_percent': None,
                'error': str(e)
            }
    
    def get_stock_history(self, stock_code: str, period: str = "30", 
                         adjust: str = "qfq") -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            period: 获取天数，默认30天
            adjust: 复权类型，qfq-前复权，hfq-后复权，""不复权
            
        Returns:
            包含历史数据的DataFrame
        """
        cache_key = self._get_cache_key(stock_code, f'history_{period}_{adjust}')
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # 计算开始日期
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=int(period))).strftime('%Y%m%d')
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if df.empty:
                logger.warning(f"股票 {stock_code} 历史数据为空")
                return pd.DataFrame()
            
            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            })
            
            # 确保数据类型正确
            numeric_columns = ['open', 'close', 'high', 'low', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 按日期排序
            df = df.sort_values('date').reset_index(drop=True)
            
            # 缓存结果
            self.cache[cache_key] = {
                'data': df,
                'timestamp': time.time()
            }
            
            logger.info(f"获取股票 {stock_code} 历史数据成功，共 {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_market_status(self) -> Dict:
        """
        获取市场状态
        
        Returns:
            市场状态信息
        """
        try:
            # 获取当前时间
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            
            # 判断是否为交易日（简单判断，不考虑节假日）
            is_weekday = now.weekday() < 5
            
            # 判断是否在交易时间
            morning_start = '09:30'
            morning_end = '11:30'
            afternoon_start = '13:00'
            afternoon_end = '15:00'
            
            is_trading_time = (
                is_weekday and (
                    (morning_start <= current_time <= morning_end) or
                    (afternoon_start <= current_time <= afternoon_end)
                )
            )
            
            return {
                'is_trading_day': is_weekday,
                'is_trading_time': is_trading_time,
                'current_time': current_time,
                'market_status': 'open' if is_trading_time else 'closed'
            }
            
        except Exception as e:
            logger.error(f"获取市场状态失败: {e}")
            return {
                'is_trading_day': False,
                'is_trading_time': False,
                'current_time': datetime.now().strftime('%H:%M'),
                'market_status': 'unknown',
                'error': str(e)
            }


# 全局数据提供者实例
stock_data_provider = StockDataProvider()
