"""
测试股票600132的分析功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stock_data import stock_data_provider
from technical_analysis import technical_analyzer

def test_stock_600132():
    """测试股票600132"""
    stock_code = "600132"
    print(f"🔍 开始分析股票 {stock_code}...")
    print("=" * 60)
    
    # 1. 获取股票基本信息
    print("📈 获取股票基本信息:")
    stock_info = stock_data_provider.get_stock_info(stock_code)
    
    print(f"股票代码: {stock_info['code']}")
    print(f"股票名称: {stock_info['name']}")
    print(f"所属市场: {stock_info['market']}")
    
    if stock_info['current_price'] is not None:
        print(f"当前价格: {stock_info['current_price']:.2f} 元")
        print(f"涨跌额: {stock_info['change']:.2f} 元")
        print(f"涨跌幅: {stock_info['change_percent']:.2f}%")
    else:
        print("当前价格: 暂无数据（可能是非交易时间）")
    
    if 'error' in stock_info:
        print(f"⚠️ 获取实时数据时遇到问题: {stock_info['error']}")
    
    print("\n" + "=" * 60)
    
    # 2. 获取历史数据
    print("📊 获取历史数据 (最近30天):")
    df = stock_data_provider.get_stock_history(stock_code, "30")
    
    if df.empty:
        print("❌ 无法获取历史数据")
        return
    
    print(f"✅ 成功获取 {len(df)} 天的历史数据")
    print("\n最近5天的交易数据:")
    recent_data = df.tail(5)
    
    for _, row in recent_data.iterrows():
        print(f"📅 {row['date']}")
        print(f"   开盘: {row['open']:.2f}  收盘: {row['close']:.2f}")
        print(f"   最高: {row['high']:.2f}  最低: {row['low']:.2f}")
        print(f"   成交量: {row['volume']:,.0f}")
        print()
    
    print("=" * 60)
    
    # 3. 技术分析
    print("🔍 技术分析报告:")
    analysis = technical_analyzer.comprehensive_analysis(df)
    
    if 'error' in analysis:
        print(f"❌ 技术分析失败: {analysis['error']}")
        return
    
    # 趋势分析
    trend_emoji = "📈" if analysis['trend'] == "上升" else "📉" if analysis['trend'] == "下降" else "📊"
    print(f"{trend_emoji} 趋势分析: {analysis['trend']}")
    print()
    
    # 移动平均线
    print("📈 移动平均线:")
    if analysis['ma5'] is not None:
        print(f"   MA5:  {analysis['ma5']:.2f} 元")
    if analysis['ma10'] is not None:
        print(f"   MA10: {analysis['ma10']:.2f} 元")
    if analysis['ma20'] is not None:
        print(f"   MA20: {analysis['ma20']:.2f} 元")
    if analysis['ma60'] is not None:
        print(f"   MA60: {analysis['ma60']:.2f} 元")
    print()
    
    # MACD指标
    print("📊 MACD指标:")
    if analysis['macd'] is not None:
        print(f"   MACD线: {analysis['macd']:.4f}")
        print(f"   信号线: {analysis['macd_signal']:.4f}")
        print(f"   柱状图: {analysis['macd_histogram']:.4f}")
        
        # MACD信号判断
        if analysis['macd'] > analysis['macd_signal']:
            print("   📈 MACD金叉，看涨信号")
        else:
            print("   📉 MACD死叉，看跌信号")
    print()
    
    # RSI指标
    print("🎯 RSI指标:")
    if analysis['rsi'] is not None:
        rsi_value = analysis['rsi']
        print(f"   RSI: {rsi_value:.2f}")
        
        if rsi_value >= 80:
            print("   🔴 超买区域，可能回调")
        elif rsi_value >= 70:
            print("   🟡 偏高区域，注意风险")
        elif rsi_value <= 20:
            print("   🟢 超卖区域，可能反弹")
        elif rsi_value <= 30:
            print("   🟡 偏低区域，关注机会")
        else:
            print("   ⚪ 正常区域")
    print()
    
    # KDJ指标
    print("⚡ KDJ指标:")
    if all(x is not None for x in [analysis['kdj_k'], analysis['kdj_d'], analysis['kdj_j']]):
        print(f"   K: {analysis['kdj_k']:.2f}")
        print(f"   D: {analysis['kdj_d']:.2f}")
        print(f"   J: {analysis['kdj_j']:.2f}")
        
        if analysis['kdj_k'] > analysis['kdj_d']:
            print("   📈 KDJ金叉")
        else:
            print("   📉 KDJ死叉")
    print()
    
    # 布林带
    print("📊 布林带:")
    if all(x is not None for x in [analysis['bollinger_upper'], analysis['bollinger_middle'], analysis['bollinger_lower']]):
        current_price = df['close'].iloc[-1]
        upper = analysis['bollinger_upper']
        middle = analysis['bollinger_middle']
        lower = analysis['bollinger_lower']
        
        print(f"   上轨: {upper:.2f} 元")
        print(f"   中轨: {middle:.2f} 元")
        print(f"   下轨: {lower:.2f} 元")
        
        if current_price > upper:
            print("   🔴 价格突破上轨，可能超买")
        elif current_price < lower:
            print("   🟢 价格跌破下轨，可能超卖")
        else:
            print("   ⚪ 价格在布林带内正常波动")
    print()
    
    # 支撑阻力位
    print("🎯 关键价位:")
    if analysis['support_levels']:
        support_str = ', '.join([f'{level:.2f}' for level in analysis['support_levels']])
        print(f"   📉 支撑位: {support_str} 元")
    
    if analysis['resistance_levels']:
        resistance_str = ', '.join([f'{level:.2f}' for level in analysis['resistance_levels']])
        print(f"   📈 阻力位: {resistance_str} 元")
    
    print("\n" + "=" * 60)
    
    # 4. 综合评估
    print("📝 综合评估:")
    
    # 计算一些基本统计
    current_price = df['close'].iloc[-1]
    price_change_5d = ((current_price - df['close'].iloc[-6]) / df['close'].iloc[-6] * 100) if len(df) >= 6 else None
    price_change_10d = ((current_price - df['close'].iloc[-11]) / df['close'].iloc[-11] * 100) if len(df) >= 11 else None
    
    if price_change_5d is not None:
        print(f"📊 5日涨跌幅: {price_change_5d:.2f}%")
    if price_change_10d is not None:
        print(f"📊 10日涨跌幅: {price_change_10d:.2f}%")
    
    # 成交量分析
    avg_volume = df['volume'].tail(10).mean()
    recent_volume = df['volume'].iloc[-1]
    volume_ratio = recent_volume / avg_volume
    
    print(f"📊 成交量比率: {volume_ratio:.2f} (最新/10日均值)")
    if volume_ratio > 1.5:
        print("   🔥 成交量放大，关注度较高")
    elif volume_ratio < 0.5:
        print("   💤 成交量萎缩，关注度较低")
    else:
        print("   ⚪ 成交量正常")
    
    print(f"\n📊 分析基于最近 {len(df)} 天的交易数据")
    print("⚠️ 以上分析仅供参考，投资有风险，决策需谨慎！")

def main():
    """主函数"""
    try:
        test_stock_600132()
        print("\n✅ 股票600132分析完成！")
        
    except Exception as e:
        print(f"\n❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
