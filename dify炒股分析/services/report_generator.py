"""
分析报告生成服务
"""
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """分析报告生成器"""
    
    def __init__(self):
        pass
    
    def generate_analysis_report(self, stock_info: Dict, technical_indicators: Dict, 
                               recent_data: List[Dict]) -> Dict[str, str]:
        """
        生成股票分析报告
        
        Args:
            stock_info: 股票基础信息
            technical_indicators: 技术指标数据
            recent_data: 最近交易数据
            
        Returns:
            Dict: 包含各类分析的报告字典
        """
        try:
            report = {
                'trend_analysis': self._generate_trend_analysis(technical_indicators, recent_data),
                'volume_analysis': self._generate_volume_analysis(recent_data),
                'risk_assessment': self._generate_risk_assessment(technical_indicators),
                'support_resistance': self._generate_support_resistance_analysis(technical_indicators),
                'trading_suggestion': self._generate_trading_suggestion(stock_info, technical_indicators)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"生成分析报告失败: {str(e)}")
            return self._get_default_report()
    
    def _generate_trend_analysis(self, indicators: Dict, recent_data: List[Dict]) -> str:
        """生成趋势分析"""
        try:
            trend = indicators.get('trend', '未知')
            ma5 = indicators.get('ma5')
            ma20 = indicators.get('ma20')
            ma60 = indicators.get('ma60')
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            
            analysis = f"当前股票趋势判断为：{trend}。"
            
            # 均线分析
            if ma5 and ma20:
                if ma5 > ma20:
                    analysis += f"短期均线MA5({ma5:.2f})位于中期均线MA20({ma20:.2f})之上，显示短期上升动能。"
                else:
                    analysis += f"短期均线MA5({ma5:.2f})位于中期均线MA20({ma20:.2f})之下，显示短期下降压力。"
            
            if ma20 and ma60:
                if ma20 > ma60:
                    analysis += f"中期均线MA20({ma20:.2f})位于长期均线MA60({ma60:.2f})之上，中长期趋势向好。"
                else:
                    analysis += f"中期均线MA20({ma20:.2f})位于长期均线MA60({ma60:.2f})之下，中长期趋势偏弱。"
            
            # MACD分析
            if macd is not None and macd_signal is not None:
                if macd > macd_signal:
                    analysis += f"MACD指标({macd:.3f})位于信号线({macd_signal:.3f})之上，技术面偏强。"
                else:
                    analysis += f"MACD指标({macd:.3f})位于信号线({macd_signal:.3f})之下，技术面偏弱。"
            
            # 价格走势分析
            if recent_data and len(recent_data) >= 5:
                recent_closes = [data['close'] for data in recent_data[-5:]]
                if recent_closes[-1] > recent_closes[0]:
                    analysis += "近5日价格呈现上升态势。"
                else:
                    analysis += "近5日价格呈现下降态势。"
            
            return analysis
            
        except Exception as e:
            logger.error(f"生成趋势分析失败: {str(e)}")
            return "趋势分析暂时无法生成，请稍后重试。"
    
    def _generate_volume_analysis(self, recent_data: List[Dict]) -> str:
        """生成成交量分析"""
        try:
            if not recent_data or len(recent_data) < 5:
                return "成交量数据不足，无法进行分析。"
            
            # 计算最近5日平均成交量
            recent_volumes = [data['volume'] for data in recent_data[-5:] if data['volume']]
            if not recent_volumes:
                return "成交量数据缺失，无法进行分析。"
            
            avg_volume = sum(recent_volumes) / len(recent_volumes)
            latest_volume = recent_volumes[-1]
            
            analysis = f"最新成交量为{latest_volume:,}手，"
            
            if latest_volume > avg_volume * 1.5:
                analysis += "较近期平均水平显著放大，表明市场关注度提升，资金活跃度增强。"
            elif latest_volume > avg_volume * 1.2:
                analysis += "较近期平均水平温和放大，显示适度的市场参与度。"
            elif latest_volume < avg_volume * 0.7:
                analysis += "较近期平均水平明显萎缩，市场参与度较低，观望情绪浓厚。"
            else:
                analysis += "与近期平均水平基本持平，市场参与度正常。"
            
            # 量价关系分析
            if len(recent_data) >= 2:
                price_change = recent_data[-1]['close'] - recent_data[-2]['close']
                volume_change = latest_volume - recent_volumes[-2] if len(recent_volumes) >= 2 else 0
                
                if price_change > 0 and volume_change > 0:
                    analysis += "价涨量增，属于健康的上涨形态。"
                elif price_change > 0 and volume_change < 0:
                    analysis += "价涨量缩，上涨动能可能不足。"
                elif price_change < 0 and volume_change > 0:
                    analysis += "价跌量增，可能存在抛压。"
                else:
                    analysis += "价跌量缩，下跌动能减弱。"
            
            return analysis
            
        except Exception as e:
            logger.error(f"生成成交量分析失败: {str(e)}")
            return "成交量分析暂时无法生成，请稍后重试。"
    
    def _generate_risk_assessment(self, indicators: Dict) -> str:
        """生成风险评估"""
        try:
            risk_level = "中等"
            risk_factors = []
            
            # RSI风险评估
            rsi = indicators.get('rsi')
            if rsi is not None:
                if rsi > 80:
                    risk_factors.append(f"RSI指标达到{rsi:.1f}，处于严重超买区域，存在较高回调风险")
                    risk_level = "较高"
                elif rsi > 70:
                    risk_factors.append(f"RSI指标达到{rsi:.1f}，接近超买区域，需注意回调风险")
                elif rsi < 20:
                    risk_factors.append(f"RSI指标为{rsi:.1f}，处于严重超卖区域，可能存在反弹机会")
                elif rsi < 30:
                    risk_factors.append(f"RSI指标为{rsi:.1f}，接近超卖区域，下跌空间有限")
            
            # KDJ风险评估
            kdj_j = indicators.get('kdj_j')
            if kdj_j is not None:
                if kdj_j > 100:
                    risk_factors.append(f"KDJ的J值达到{kdj_j:.1f}，超买信号强烈")
                    if risk_level == "中等":
                        risk_level = "较高"
                elif kdj_j < 0:
                    risk_factors.append(f"KDJ的J值为{kdj_j:.1f}，超卖信号明显")
            
            # 布林带风险评估
            bollinger_upper = indicators.get('bollinger_upper')
            bollinger_lower = indicators.get('bollinger_lower')
            if bollinger_upper and bollinger_lower:
                # 这里需要当前价格来判断，暂时跳过
                pass
            
            # 趋势风险评估
            trend = indicators.get('trend', '')
            if trend == "下降":
                risk_factors.append("当前处于下降趋势，存在继续下跌风险")
                if risk_level == "中等":
                    risk_level = "较高"
            
            # 生成风险评估报告
            assessment = f"综合风险评估等级：{risk_level}。"
            
            if risk_factors:
                assessment += "主要风险因素包括：" + "；".join(risk_factors) + "。"
            else:
                assessment += "当前技术指标未显示明显的极端风险信号。"
            
            # 风险建议
            if risk_level == "较高":
                assessment += "建议谨慎操作，控制仓位，设置止损。"
            elif risk_level == "较低":
                assessment += "风险相对可控，可适当参与。"
            else:
                assessment += "建议保持正常的风险控制措施。"
            
            return assessment
            
        except Exception as e:
            logger.error(f"生成风险评估失败: {str(e)}")
            return "风险评估暂时无法生成，请稍后重试。"
    
    def _generate_support_resistance_analysis(self, indicators: Dict) -> str:
        """生成支撑阻力分析"""
        try:
            support_levels = indicators.get('support_levels', [])
            resistance_levels = indicators.get('resistance_levels', [])
            
            analysis = ""
            
            if support_levels:
                support_str = "、".join([f"{level:.2f}元" for level in support_levels])
                analysis += f"技术支撑位位于：{support_str}。"
            else:
                analysis += "暂未识别到明确的技术支撑位。"
            
            if resistance_levels:
                resistance_str = "、".join([f"{level:.2f}元" for level in resistance_levels])
                analysis += f"技术阻力位位于：{resistance_str}。"
            else:
                analysis += "暂未识别到明确的技术阻力位。"
            
            # 布林带支撑阻力
            bollinger_upper = indicators.get('bollinger_upper')
            bollinger_lower = indicators.get('bollinger_lower')
            if bollinger_upper and bollinger_lower:
                analysis += f"布林带上轨{bollinger_upper:.2f}元构成动态阻力，下轨{bollinger_lower:.2f}元构成动态支撑。"
            
            # 均线支撑阻力
            ma20 = indicators.get('ma20')
            ma60 = indicators.get('ma60')
            if ma20:
                analysis += f"20日均线{ma20:.2f}元可作为重要的支撑/阻力参考。"
            if ma60:
                analysis += f"60日均线{ma60:.2f}元为中长期支撑/阻力位。"
            
            return analysis
            
        except Exception as e:
            logger.error(f"生成支撑阻力分析失败: {str(e)}")
            return "支撑阻力分析暂时无法生成，请稍后重试。"
    
    def _generate_trading_suggestion(self, stock_info: Dict, indicators: Dict) -> str:
        """生成交易建议"""
        try:
            trend = indicators.get('trend', '')
            rsi = indicators.get('rsi')
            kdj_j = indicators.get('kdj_j')
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            support_levels = indicators.get('support_levels', [])
            
            suggestion = ""
            
            # 基于趋势的建议
            if trend == "上升":
                suggestion += "当前处于上升趋势，可考虑逢低买入。"
            elif trend == "下降":
                suggestion += "当前处于下降趋势，建议观望或减仓。"
            else:
                suggestion += "当前处于震荡行情，建议高抛低吸。"
            
            # 基于超买超卖的建议
            if rsi is not None:
                if rsi > 70:
                    suggestion += f"RSI({rsi:.1f})显示超买，建议等待回调后再考虑买入。"
                elif rsi < 30:
                    suggestion += f"RSI({rsi:.1f})显示超卖，可关注反弹机会。"
            
            # 基于MACD的建议
            if macd is not None and macd_signal is not None:
                if macd > macd_signal and macd > 0:
                    suggestion += "MACD金叉且位于零轴上方，技术面偏强。"
                elif macd < macd_signal and macd < 0:
                    suggestion += "MACD死叉且位于零轴下方，技术面偏弱。"
            
            # 止损建议
            if support_levels:
                nearest_support = min(support_levels)
                suggestion += f"建议将止损位设置在{nearest_support:.2f}元附近。"
            
            # 风险提示
            suggestion += "以上建议仅供参考，投资有风险，请根据自身风险承受能力谨慎决策。"
            
            return suggestion
            
        except Exception as e:
            logger.error(f"生成交易建议失败: {str(e)}")
            return "交易建议暂时无法生成，请稍后重试。"
    
    def _get_default_report(self) -> Dict[str, str]:
        """获取默认报告"""
        return {
            'trend_analysis': "趋势分析暂时无法生成，请稍后重试。",
            'volume_analysis': "成交量分析暂时无法生成，请稍后重试。",
            'risk_assessment': "风险评估暂时无法生成，请稍后重试。",
            'support_resistance': "支撑阻力分析暂时无法生成，请稍后重试。",
            'trading_suggestion': "交易建议暂时无法生成，请稍后重试。"
        }


# 创建全局报告生成器实例
report_generator = ReportGenerator()
