"""
股票分析功能测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 导入要测试的模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from stock_data import StockDataProvider
from technical_analysis import TechnicalAnalyzer
from utils import validate_stock_code, normalize_stock_code, get_market_from_code


class TestStockDataProvider:
    """测试股票数据提供者"""
    
    def setup_method(self):
        """设置测试环境"""
        self.provider = StockDataProvider()
    
    def test_get_stock_info(self):
        """测试获取股票信息"""
        # 测试有效股票代码
        result = self.provider.get_stock_info("000001")
        
        assert 'code' in result
        assert 'name' in result
        assert 'market' in result
        assert result['code'] == "000001"
    
    def test_get_stock_history(self):
        """测试获取历史数据"""
        df = self.provider.get_stock_history("000001", "10")
        
        # 检查返回的DataFrame结构
        if not df.empty:
            expected_columns = ['date', 'open', 'close', 'high', 'low', 'volume']
            for col in expected_columns:
                assert col in df.columns
    
    def test_get_market_status(self):
        """测试获取市场状态"""
        status = self.provider.get_market_status()
        
        assert 'is_trading_day' in status
        assert 'is_trading_time' in status
        assert 'current_time' in status
        assert 'market_status' in status


class TestTechnicalAnalyzer:
    """测试技术分析器"""
    
    def setup_method(self):
        """设置测试环境"""
        self.analyzer = TechnicalAnalyzer()
        
        # 创建测试数据
        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
        np.random.seed(42)
        
        # 生成模拟股价数据
        base_price = 10.0
        price_changes = np.random.normal(0, 0.02, 50)
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 0.1))  # 确保价格为正
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': [p * 0.99 for p in prices],
            'close': prices,
            'high': [p * 1.02 for p in prices],
            'low': [p * 0.98 for p in prices],
            'volume': np.random.randint(1000000, 10000000, 50)
        })
    
    def test_calculate_ma(self):
        """测试移动平均线计算"""
        close_prices = pd.Series(self.test_data['close'])
        ma5 = self.analyzer.calculate_ma(close_prices, 5)
        
        assert len(ma5) == len(close_prices)
        assert not ma5.iloc[-1] != ma5.iloc[-1]  # 检查不是NaN
    
    def test_calculate_macd(self):
        """测试MACD计算"""
        close_prices = pd.Series(self.test_data['close'])
        macd_data = self.analyzer.calculate_macd(close_prices)
        
        assert 'macd' in macd_data
        assert 'signal' in macd_data
        assert 'histogram' in macd_data
        assert len(macd_data['macd']) == len(close_prices)
    
    def test_calculate_rsi(self):
        """测试RSI计算"""
        close_prices = pd.Series(self.test_data['close'])
        rsi = self.analyzer.calculate_rsi(close_prices)
        
        assert len(rsi) == len(close_prices)
        # RSI应该在0-100之间
        valid_rsi = rsi.dropna()
        if not valid_rsi.empty:
            assert all(0 <= val <= 100 for val in valid_rsi)
    
    def test_calculate_kdj(self):
        """测试KDJ计算"""
        high = pd.Series(self.test_data['high'])
        low = pd.Series(self.test_data['low'])
        close = pd.Series(self.test_data['close'])
        
        kdj_data = self.analyzer.calculate_kdj(high, low, close)
        
        assert 'k' in kdj_data
        assert 'd' in kdj_data
        assert 'j' in kdj_data
        assert len(kdj_data['k']) == len(close)
    
    def test_calculate_bollinger_bands(self):
        """测试布林带计算"""
        close_prices = pd.Series(self.test_data['close'])
        bb_data = self.analyzer.calculate_bollinger_bands(close_prices)
        
        assert 'upper' in bb_data
        assert 'middle' in bb_data
        assert 'lower' in bb_data
        assert len(bb_data['upper']) == len(close_prices)
    
    def test_find_support_resistance(self):
        """测试支撑阻力位寻找"""
        high = pd.Series(self.test_data['high'])
        low = pd.Series(self.test_data['low'])
        close = pd.Series(self.test_data['close'])
        
        sr_data = self.analyzer.find_support_resistance(high, low, close)
        
        assert 'support_levels' in sr_data
        assert 'resistance_levels' in sr_data
        assert isinstance(sr_data['support_levels'], list)
        assert isinstance(sr_data['resistance_levels'], list)
    
    def test_analyze_trend(self):
        """测试趋势分析"""
        close_prices = pd.Series(self.test_data['close'])
        trend = self.analyzer.analyze_trend(close_prices)
        
        assert trend in ['上升', '下降', '震荡', '数据不足', '未知']
    
    def test_comprehensive_analysis(self):
        """测试综合分析"""
        analysis = self.analyzer.comprehensive_analysis(self.test_data)
        
        # 检查返回的分析结果包含必要字段
        expected_fields = [
            'trend', 'ma5', 'ma10', 'ma20',
            'macd', 'macd_signal', 'macd_histogram',
            'rsi', 'support_levels', 'resistance_levels'
        ]
        
        for field in expected_fields:
            assert field in analysis


class TestUtils:
    """测试工具函数"""
    
    def test_validate_stock_code(self):
        """测试股票代码验证"""
        assert validate_stock_code("000001") == True
        assert validate_stock_code("600000") == True
        assert validate_stock_code("12345") == False
        assert validate_stock_code("1234567") == False
        assert validate_stock_code("abcdef") == False
        assert validate_stock_code("") == False
        assert validate_stock_code(None) == False
    
    def test_normalize_stock_code(self):
        """测试股票代码标准化"""
        assert normalize_stock_code("000001") == "000001"
        assert normalize_stock_code("1") == "000001"
        assert normalize_stock_code("SZ000001") == "000001"
        assert normalize_stock_code("000001.SZ") == "000001"
        assert normalize_stock_code("1234567") == "123456"
    
    def test_get_market_from_code(self):
        """测试根据代码判断市场"""
        assert get_market_from_code("000001") == "深圳"
        assert get_market_from_code("300001") == "深圳"
        assert get_market_from_code("600000") == "上海"
        assert get_market_from_code("800001") == "北京"
        assert get_market_from_code("123456") == "其他"
        assert get_market_from_code("12345") == "未知"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
