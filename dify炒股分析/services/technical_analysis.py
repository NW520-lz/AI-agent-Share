"""
技术指标计算模块
"""
import pandas as pd
import numpy as np
try:
    import talib
    HAS_TALIB = True
except ImportError:
    HAS_TALIB = False
    print("警告: talib未安装，将使用pandas实现技术指标计算")
from typing import Dict, List, Tuple, Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class TechnicalAnalysis:
    """技术指标计算类"""
    
    def __init__(self):
        self.ma_periods = settings.MA_PERIODS
        self.macd_fast = settings.MACD_FAST
        self.macd_slow = settings.MACD_SLOW
        self.macd_signal = settings.MACD_SIGNAL
        self.rsi_period = settings.RSI_PERIOD
        self.kdj_period = settings.KDJ_PERIOD
        self.bollinger_period = settings.BOLLINGER_PERIOD
        self.bollinger_std = settings.BOLLINGER_STD
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict:
        """
        计算所有技术指标
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            Dict: 包含所有技术指标的字典
        """
        try:
            if df.empty or len(df) < 20:
                logger.warning("数据不足，无法计算技术指标")
                return self._get_empty_indicators()
            
            # 确保数据格式正确
            df = self._prepare_data(df)
            
            # 计算各种技术指标
            indicators = {}
            
            # 移动平均线
            indicators.update(self._calculate_moving_averages(df))
            
            # MACD指标
            indicators.update(self._calculate_macd(df))
            
            # KDJ指标
            indicators.update(self._calculate_kdj(df))
            
            # RSI指标
            indicators.update(self._calculate_rsi(df))
            
            # 布林带
            indicators.update(self._calculate_bollinger_bands(df))
            
            # 支撑阻力位
            indicators.update(self._calculate_support_resistance(df))
            
            # 趋势判断
            indicators['trend'] = self._determine_trend(df, indicators)
            
            return indicators
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {str(e)}")
            return self._get_empty_indicators()
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备数据格式"""
        # 确保列名标准化
        column_mapping = {
            '开盘': 'open', '收盘': 'close', '最高': 'high', 
            '最低': 'low', '成交量': 'volume'
        }
        
        # 重命名列
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # 确保数据类型正确
        for col in ['open', 'close', 'high', 'low']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # 按日期排序
        if '日期' in df.columns:
            df = df.sort_values('日期')
        
        return df
    
    def _calculate_moving_averages(self, df: pd.DataFrame) -> Dict:
        """计算移动平均线"""
        ma_data = {}

        try:
            if HAS_TALIB:
                close_prices = df['close'].values
                for period in self.ma_periods:
                    if len(close_prices) >= period:
                        ma = talib.SMA(close_prices, timeperiod=period)
                        ma_data[f'ma{period}'] = float(ma[-1]) if not np.isnan(ma[-1]) else None
                    else:
                        ma_data[f'ma{period}'] = None
            else:
                # 使用pandas计算移动平均线
                for period in self.ma_periods:
                    if len(df) >= period:
                        ma = df['close'].rolling(window=period).mean()
                        ma_data[f'ma{period}'] = float(ma.iloc[-1]) if not pd.isna(ma.iloc[-1]) else None
                    else:
                        ma_data[f'ma{period}'] = None

        except Exception as e:
            logger.error(f"计算移动平均线失败: {str(e)}")
            for period in self.ma_periods:
                ma_data[f'ma{period}'] = None

        return ma_data
    
    def _calculate_macd(self, df: pd.DataFrame) -> Dict:
        """计算MACD指标"""
        try:
            close_prices = df['close'].values
            
            if len(close_prices) >= max(self.macd_fast, self.macd_slow) + self.macd_signal:
                macd, macd_signal, macd_hist = talib.MACD(
                    close_prices,
                    fastperiod=self.macd_fast,
                    slowperiod=self.macd_slow,
                    signalperiod=self.macd_signal
                )
                
                return {
                    'macd': float(macd[-1]) if not np.isnan(macd[-1]) else None,
                    'macd_signal': float(macd_signal[-1]) if not np.isnan(macd_signal[-1]) else None,
                    'macd_histogram': float(macd_hist[-1]) if not np.isnan(macd_hist[-1]) else None
                }
            else:
                return {
                    'macd': None,
                    'macd_signal': None,
                    'macd_histogram': None
                }
                
        except Exception as e:
            logger.error(f"计算MACD失败: {str(e)}")
            return {
                'macd': None,
                'macd_signal': None,
                'macd_histogram': None
            }
    
    def _calculate_kdj(self, df: pd.DataFrame) -> Dict:
        """计算KDJ指标"""
        try:
            high_prices = df['high'].values
            low_prices = df['low'].values
            close_prices = df['close'].values
            
            if len(close_prices) >= self.kdj_period:
                # 计算KDJ
                k, d = talib.STOCH(
                    high_prices, low_prices, close_prices,
                    fastk_period=self.kdj_period,
                    slowk_period=3,
                    slowd_period=3
                )
                
                # J值计算：J = 3K - 2D
                j = 3 * k - 2 * d
                
                return {
                    'kdj_k': float(k[-1]) if not np.isnan(k[-1]) else None,
                    'kdj_d': float(d[-1]) if not np.isnan(d[-1]) else None,
                    'kdj_j': float(j[-1]) if not np.isnan(j[-1]) else None
                }
            else:
                return {
                    'kdj_k': None,
                    'kdj_d': None,
                    'kdj_j': None
                }
                
        except Exception as e:
            logger.error(f"计算KDJ失败: {str(e)}")
            return {
                'kdj_k': None,
                'kdj_d': None,
                'kdj_j': None
            }
    
    def _calculate_rsi(self, df: pd.DataFrame) -> Dict:
        """计算RSI指标"""
        try:
            close_prices = df['close'].values
            
            if len(close_prices) >= self.rsi_period + 1:
                rsi = talib.RSI(close_prices, timeperiod=self.rsi_period)
                return {
                    'rsi': float(rsi[-1]) if not np.isnan(rsi[-1]) else None
                }
            else:
                return {'rsi': None}
                
        except Exception as e:
            logger.error(f"计算RSI失败: {str(e)}")
            return {'rsi': None}
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame) -> Dict:
        """计算布林带"""
        try:
            close_prices = df['close'].values
            
            if len(close_prices) >= self.bollinger_period:
                upper, middle, lower = talib.BBANDS(
                    close_prices,
                    timeperiod=self.bollinger_period,
                    nbdevup=self.bollinger_std,
                    nbdevdn=self.bollinger_std
                )
                
                return {
                    'bollinger_upper': float(upper[-1]) if not np.isnan(upper[-1]) else None,
                    'bollinger_middle': float(middle[-1]) if not np.isnan(middle[-1]) else None,
                    'bollinger_lower': float(lower[-1]) if not np.isnan(lower[-1]) else None
                }
            else:
                return {
                    'bollinger_upper': None,
                    'bollinger_middle': None,
                    'bollinger_lower': None
                }
                
        except Exception as e:
            logger.error(f"计算布林带失败: {str(e)}")
            return {
                'bollinger_upper': None,
                'bollinger_middle': None,
                'bollinger_lower': None
            }
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """计算支撑阻力位"""
        try:
            if len(df) < 10:
                return {
                    'support_levels': [],
                    'resistance_levels': []
                }
            
            # 获取最近20天的高低点
            recent_data = df.tail(20)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            
            # 简单的支撑阻力位计算
            # 支撑位：最近的低点
            support_levels = []
            resistance_levels = []
            
            # 找出局部低点作为支撑位
            for i in range(2, len(lows) - 2):
                if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and 
                    lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                    support_levels.append(float(lows[i]))
            
            # 找出局部高点作为阻力位
            for i in range(2, len(highs) - 2):
                if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and 
                    highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                    resistance_levels.append(float(highs[i]))
            
            # 去重并排序
            support_levels = sorted(list(set(support_levels)))[-3:]  # 最多3个支撑位
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:3]  # 最多3个阻力位
            
            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels
            }
            
        except Exception as e:
            logger.error(f"计算支撑阻力位失败: {str(e)}")
            return {
                'support_levels': [],
                'resistance_levels': []
            }
    
    def _determine_trend(self, df: pd.DataFrame, indicators: Dict) -> str:
        """判断趋势"""
        try:
            if len(df) < 5:
                return "数据不足"
            
            # 基于多个指标综合判断趋势
            trend_signals = []
            
            # 1. 基于移动平均线
            if indicators.get('ma5') and indicators.get('ma20'):
                if indicators['ma5'] > indicators['ma20']:
                    trend_signals.append(1)  # 上升
                else:
                    trend_signals.append(-1)  # 下降
            
            # 2. 基于MACD
            if indicators.get('macd') and indicators.get('macd_signal'):
                if indicators['macd'] > indicators['macd_signal']:
                    trend_signals.append(1)
                else:
                    trend_signals.append(-1)
            
            # 3. 基于价格趋势
            recent_closes = df['close'].tail(5).values
            if len(recent_closes) >= 5:
                if recent_closes[-1] > recent_closes[0]:
                    trend_signals.append(1)
                else:
                    trend_signals.append(-1)
            
            # 综合判断
            if not trend_signals:
                return "震荡"
            
            avg_signal = sum(trend_signals) / len(trend_signals)
            
            if avg_signal > 0.3:
                return "上升"
            elif avg_signal < -0.3:
                return "下降"
            else:
                return "震荡"
                
        except Exception as e:
            logger.error(f"判断趋势失败: {str(e)}")
            return "未知"
    
    def _get_empty_indicators(self) -> Dict:
        """返回空的技术指标字典"""
        return {
            'trend': '数据不足',
            'ma5': None,
            'ma10': None,
            'ma20': None,
            'ma60': None,
            'macd': None,
            'macd_signal': None,
            'macd_histogram': None,
            'kdj_k': None,
            'kdj_d': None,
            'kdj_j': None,
            'rsi': None,
            'bollinger_upper': None,
            'bollinger_middle': None,
            'bollinger_lower': None,
            'support_levels': [],
            'resistance_levels': []
        }


# 创建全局技术分析实例
technical_analysis = TechnicalAnalysis()
