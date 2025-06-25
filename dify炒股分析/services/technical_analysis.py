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
                if HAS_TALIB:
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
                    # 使用pandas实现MACD
                    close_series = pd.Series(close_prices)

                    # 计算EMA
                    ema_fast = close_series.ewm(span=self.macd_fast).mean()
                    ema_slow = close_series.ewm(span=self.macd_slow).mean()

                    # MACD线 = 快线EMA - 慢线EMA
                    macd_line = ema_fast - ema_slow

                    # 信号线 = MACD线的EMA
                    signal_line = macd_line.ewm(span=self.macd_signal).mean()

                    # 柱状图 = MACD线 - 信号线
                    histogram = macd_line - signal_line

                    return {
                        'macd': float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
                        'macd_signal': float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None,
                        'macd_histogram': float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None
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
                if HAS_TALIB:
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
                    # 使用pandas实现KDJ
                    high_series = pd.Series(high_prices)
                    low_series = pd.Series(low_prices)
                    close_series = pd.Series(close_prices)

                    # 计算RSV (Raw Stochastic Value)
                    lowest_low = low_series.rolling(window=self.kdj_period).min()
                    highest_high = high_series.rolling(window=self.kdj_period).max()
                    rsv = (close_series - lowest_low) / (highest_high - lowest_low) * 100

                    # 计算K值：K = 2/3 * 前一日K值 + 1/3 * 当日RSV
                    k_values = []
                    k_prev = 50  # K值初始值
                    for rsv_val in rsv:
                        if pd.isna(rsv_val):
                            k_values.append(np.nan)
                        else:
                            k_curr = (2/3) * k_prev + (1/3) * rsv_val
                            k_values.append(k_curr)
                            k_prev = k_curr

                    k_series = pd.Series(k_values)

                    # 计算D值：D = 2/3 * 前一日D值 + 1/3 * 当日K值
                    d_values = []
                    d_prev = 50  # D值初始值
                    for k_val in k_series:
                        if pd.isna(k_val):
                            d_values.append(np.nan)
                        else:
                            d_curr = (2/3) * d_prev + (1/3) * k_val
                            d_values.append(d_curr)
                            d_prev = d_curr

                    d_series = pd.Series(d_values)

                    # 计算J值：J = 3K - 2D
                    j_series = 3 * k_series - 2 * d_series

                    return {
                        'kdj_k': float(k_series.iloc[-1]) if not pd.isna(k_series.iloc[-1]) else None,
                        'kdj_d': float(d_series.iloc[-1]) if not pd.isna(d_series.iloc[-1]) else None,
                        'kdj_j': float(j_series.iloc[-1]) if not pd.isna(j_series.iloc[-1]) else None
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
                if HAS_TALIB:
                    rsi = talib.RSI(close_prices, timeperiod=self.rsi_period)
                    return {
                        'rsi': float(rsi[-1]) if not np.isnan(rsi[-1]) else None
                    }
                else:
                    # 使用pandas实现RSI
                    close_series = pd.Series(close_prices)

                    # 计算价格变化
                    delta = close_series.diff()

                    # 分离上涨和下跌
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)

                    # 计算平均收益和平均损失
                    avg_gain = gain.rolling(window=self.rsi_period).mean()
                    avg_loss = loss.rolling(window=self.rsi_period).mean()

                    # 计算RS和RSI
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))

                    return {
                        'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
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
                if HAS_TALIB:
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
                    # 使用pandas实现布林带
                    close_series = pd.Series(close_prices)

                    # 中轨：移动平均线
                    middle = close_series.rolling(window=self.bollinger_period).mean()

                    # 标准差
                    std = close_series.rolling(window=self.bollinger_period).std()

                    # 上轨和下轨
                    upper = middle + (std * self.bollinger_std)
                    lower = middle - (std * self.bollinger_std)

                    return {
                        'bollinger_upper': float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else None,
                        'bollinger_middle': float(middle.iloc[-1]) if not pd.isna(middle.iloc[-1]) else None,
                        'bollinger_lower': float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else None
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
