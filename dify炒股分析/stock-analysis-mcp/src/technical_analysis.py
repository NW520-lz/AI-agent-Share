"""
技术分析算法模块
实现各种技术指标的计算
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from loguru import logger


class TechnicalAnalyzer:
    """技术分析器"""
    
    def __init__(self):
        pass
    
    def calculate_ma(self, data: pd.Series, window: int) -> pd.Series:
        """
        计算移动平均线
        
        Args:
            data: 价格数据
            window: 窗口期
            
        Returns:
            移动平均线数据
        """
        return data.rolling(window=window).mean()
    
    def calculate_ema(self, data: pd.Series, window: int) -> pd.Series:
        """
        计算指数移动平均线
        
        Args:
            data: 价格数据
            window: 窗口期
            
        Returns:
            指数移动平均线数据
        """
        return data.ewm(span=window).mean()
    
    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, 
                      signal: int = 9) -> Dict[str, pd.Series]:
        """
        计算MACD指标
        
        Args:
            data: 收盘价数据
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
            
        Returns:
            包含MACD、信号线、柱状图的字典
        """
        try:
            ema_fast = self.calculate_ema(data, fast)
            ema_slow = self.calculate_ema(data, slow)
            
            macd_line = ema_fast - ema_slow
            signal_line = self.calculate_ema(macd_line, signal)
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
        except Exception as e:
            logger.error(f"计算MACD失败: {e}")
            return {'macd': pd.Series(), 'signal': pd.Series(), 'histogram': pd.Series()}
    
    def calculate_rsi(self, data: pd.Series, window: int = 14) -> pd.Series:
        """
        计算RSI指标
        
        Args:
            data: 收盘价数据
            window: 窗口期
            
        Returns:
            RSI数据
        """
        try:
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            logger.error(f"计算RSI失败: {e}")
            return pd.Series()
    
    def calculate_kdj(self, high: pd.Series, low: pd.Series, close: pd.Series,
                     window: int = 9, k_period: int = 3, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        计算KDJ指标
        
        Args:
            high: 最高价数据
            low: 最低价数据
            close: 收盘价数据
            window: RSV窗口期
            k_period: K值平滑周期
            d_period: D值平滑周期
            
        Returns:
            包含K、D、J值的字典
        """
        try:
            # 计算RSV
            lowest_low = low.rolling(window=window).min()
            highest_high = high.rolling(window=window).max()
            rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
            
            # 计算K值
            k = rsv.ewm(alpha=1/k_period).mean()
            
            # 计算D值
            d = k.ewm(alpha=1/d_period).mean()
            
            # 计算J值
            j = 3 * k - 2 * d
            
            return {'k': k, 'd': d, 'j': j}
        except Exception as e:
            logger.error(f"计算KDJ失败: {e}")
            return {'k': pd.Series(), 'd': pd.Series(), 'j': pd.Series()}
    
    def calculate_bollinger_bands(self, data: pd.Series, window: int = 20, 
                                 std_dev: float = 2) -> Dict[str, pd.Series]:
        """
        计算布林带
        
        Args:
            data: 收盘价数据
            window: 窗口期
            std_dev: 标准差倍数
            
        Returns:
            包含上轨、中轨、下轨的字典
        """
        try:
            middle = self.calculate_ma(data, window)
            std = data.rolling(window=window).std()
            
            upper = middle + (std * std_dev)
            lower = middle - (std * std_dev)
            
            return {
                'upper': upper,
                'middle': middle,
                'lower': lower
            }
        except Exception as e:
            logger.error(f"计算布林带失败: {e}")
            return {'upper': pd.Series(), 'middle': pd.Series(), 'lower': pd.Series()}
    
    def find_support_resistance(self, high: pd.Series, low: pd.Series, 
                               close: pd.Series, window: int = 20) -> Dict[str, List[float]]:
        """
        寻找支撑位和阻力位
        
        Args:
            high: 最高价数据
            low: 最低价数据
            close: 收盘价数据
            window: 分析窗口
            
        Returns:
            包含支撑位和阻力位的字典
        """
        try:
            # 获取最近的数据
            recent_high = high.tail(window)
            recent_low = low.tail(window)
            recent_close = close.tail(window)
            
            # 寻找局部高点和低点
            highs = []
            lows = []
            
            for i in range(2, len(recent_high) - 2):
                # 局部高点
                if (recent_high.iloc[i] > recent_high.iloc[i-1] and 
                    recent_high.iloc[i] > recent_high.iloc[i-2] and
                    recent_high.iloc[i] > recent_high.iloc[i+1] and 
                    recent_high.iloc[i] > recent_high.iloc[i+2]):
                    highs.append(recent_high.iloc[i])
                
                # 局部低点
                if (recent_low.iloc[i] < recent_low.iloc[i-1] and 
                    recent_low.iloc[i] < recent_low.iloc[i-2] and
                    recent_low.iloc[i] < recent_low.iloc[i+1] and 
                    recent_low.iloc[i] < recent_low.iloc[i+2]):
                    lows.append(recent_low.iloc[i])
            
            # 去重并排序
            resistance_levels = sorted(list(set(highs)), reverse=True)[:3]
            support_levels = sorted(list(set(lows)))[:3]
            
            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels
            }
        except Exception as e:
            logger.error(f"寻找支撑阻力位失败: {e}")
            return {'support_levels': [], 'resistance_levels': []}
    
    def analyze_trend(self, data: pd.Series, short_window: int = 5, 
                     long_window: int = 20) -> str:
        """
        分析趋势
        
        Args:
            data: 收盘价数据
            short_window: 短期窗口
            long_window: 长期窗口
            
        Returns:
            趋势描述
        """
        try:
            if len(data) < long_window:
                return "数据不足"
            
            short_ma = self.calculate_ma(data, short_window).iloc[-1]
            long_ma = self.calculate_ma(data, long_window).iloc[-1]
            current_price = data.iloc[-1]
            
            # 判断趋势
            if short_ma > long_ma and current_price > short_ma:
                return "上升"
            elif short_ma < long_ma and current_price < short_ma:
                return "下降"
            else:
                return "震荡"
                
        except Exception as e:
            logger.error(f"分析趋势失败: {e}")
            return "未知"
    
    def comprehensive_analysis(self, df: pd.DataFrame) -> Dict:
        """
        综合技术分析
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            综合分析结果
        """
        try:
            if df.empty or len(df) < 20:
                return {'error': '数据不足，无法进行技术分析'}
            
            close = df['close']
            high = df['high']
            low = df['low']
            
            # 计算各种技术指标
            ma5 = self.calculate_ma(close, 5).iloc[-1] if len(close) >= 5 else None
            ma10 = self.calculate_ma(close, 10).iloc[-1] if len(close) >= 10 else None
            ma20 = self.calculate_ma(close, 20).iloc[-1] if len(close) >= 20 else None
            ma60 = self.calculate_ma(close, 60).iloc[-1] if len(close) >= 60 else None
            
            # MACD
            macd_data = self.calculate_macd(close)
            macd = macd_data['macd'].iloc[-1] if not macd_data['macd'].empty else None
            macd_signal = macd_data['signal'].iloc[-1] if not macd_data['signal'].empty else None
            macd_histogram = macd_data['histogram'].iloc[-1] if not macd_data['histogram'].empty else None
            
            # RSI
            rsi = self.calculate_rsi(close).iloc[-1] if len(close) >= 14 else None
            
            # KDJ
            kdj_data = self.calculate_kdj(high, low, close)
            kdj_k = kdj_data['k'].iloc[-1] if not kdj_data['k'].empty else None
            kdj_d = kdj_data['d'].iloc[-1] if not kdj_data['d'].empty else None
            kdj_j = kdj_data['j'].iloc[-1] if not kdj_data['j'].empty else None
            
            # 布林带
            bb_data = self.calculate_bollinger_bands(close)
            bb_upper = bb_data['upper'].iloc[-1] if not bb_data['upper'].empty else None
            bb_middle = bb_data['middle'].iloc[-1] if not bb_data['middle'].empty else None
            bb_lower = bb_data['lower'].iloc[-1] if not bb_data['lower'].empty else None
            
            # 支撑阻力位
            sr_data = self.find_support_resistance(high, low, close)
            
            # 趋势分析
            trend = self.analyze_trend(close)
            
            return {
                'trend': trend,
                'ma5': ma5,
                'ma10': ma10,
                'ma20': ma20,
                'ma60': ma60,
                'macd': macd,
                'macd_signal': macd_signal,
                'macd_histogram': macd_histogram,
                'kdj_k': kdj_k,
                'kdj_d': kdj_d,
                'kdj_j': kdj_j,
                'rsi': rsi,
                'bollinger_upper': bb_upper,
                'bollinger_middle': bb_middle,
                'bollinger_lower': bb_lower,
                'support_levels': sr_data['support_levels'],
                'resistance_levels': sr_data['resistance_levels']
            }
            
        except Exception as e:
            logger.error(f"综合技术分析失败: {e}")
            return {'error': f'分析失败: {str(e)}'}


# 全局技术分析器实例
technical_analyzer = TechnicalAnalyzer()
