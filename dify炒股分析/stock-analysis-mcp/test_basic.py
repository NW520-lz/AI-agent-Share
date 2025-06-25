"""
基础功能测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_data import stock_data_provider
from technical_analysis import technical_analyzer

def test_stock_data():
    """测试股票数据获取"""
    print("🔍 测试股票数据获取...")
    
    # 测试获取股票信息
    print("\n📈 获取股票基本信息 (000001):")
    stock_info = stock_data_provider.get_stock_info("000001")
    print(f"股票代码: {stock_info['code']}")
    print(f"股票名称: {stock_info['name']}")
    print(f"当前价格: {stock_info['current_price']}")
    print(f"涨跌幅: {stock_info['change_percent']}%")
    
    # 测试获取历史数据
    print("\n📊 获取历史数据 (000001, 最近10天):")
    df = stock_data_provider.get_stock_history("000001", "10")
    if not df.empty:
        print(f"获取到 {len(df)} 条历史数据")
        print("最近3天数据:")
        print(df.tail(3)[['date', 'open', 'close', 'high', 'low', 'volume']])
    else:
        print("❌ 未获取到历史数据")
    
    # 测试市场状态
    print("\n🏢 市场状态:")
    market_status = stock_data_provider.get_market_status()
    print(f"市场状态: {market_status['market_status']}")
    print(f"当前时间: {market_status['current_time']}")
    print(f"是否交易时间: {market_status['is_trading_time']}")

def test_technical_analysis():
    """测试技术分析"""
    print("\n🔍 测试技术分析...")
    
    # 获取测试数据
    df = stock_data_provider.get_stock_history("000001", "30")
    
    if df.empty:
        print("❌ 无法获取历史数据，跳过技术分析测试")
        return
    
    print(f"\n📊 对股票000001进行技术分析 (基于{len(df)}天数据):")
    
    # 进行综合分析
    analysis = technical_analyzer.comprehensive_analysis(df)
    
    if 'error' in analysis:
        print(f"❌ 技术分析失败: {analysis['error']}")
        return
    
    print(f"趋势: {analysis['trend']}")
    print(f"MA5: {analysis['ma5']:.2f}")
    print(f"MA10: {analysis['ma10']:.2f}")
    print(f"MA20: {analysis['ma20']:.2f}")
    
    if analysis['rsi'] is not None:
        print(f"RSI: {analysis['rsi']:.2f}")
    
    if analysis['support_levels']:
        print(f"支撑位: {analysis['support_levels']}")
    
    if analysis['resistance_levels']:
        print(f"阻力位: {analysis['resistance_levels']}")

def main():
    """主测试函数"""
    print("🚀 开始测试股票分析MCP工具...")
    
    try:
        test_stock_data()
        test_technical_analysis()
        print("\n✅ 基础功能测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
