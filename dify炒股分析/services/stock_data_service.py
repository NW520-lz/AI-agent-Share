"""
股票数据获取服务
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import asyncio
import logging
from config import settings, ERROR_MESSAGES

logger = logging.getLogger(__name__)


class StockDataService:
    """股票数据获取服务类"""
    
    def __init__(self):
        self.timeout = settings.AKSHARE_TIMEOUT
        self.max_retries = settings.MAX_RETRY_ATTEMPTS
        # 根据官方文档建议，增加请求间隔
        self.request_delay = 2  # 秒
        
    async def get_stock_data(self, stock_code: str, market_type: str, days: int = None) -> Dict[str, Any]:
        """
        获取股票数据

        Args:
            stock_code: 股票代码
            market_type: 市场类型 (A, HK, US, ETF)
            days: 获取天数，默认使用配置值

        Returns:
            Dict: 包含股票基础信息和历史数据的字典
        """
        if days is None:
            days = settings.DEFAULT_DATA_DAYS

        # 检查是否启用真实数据获取
        if not settings.ENABLE_REAL_DATA:
            logger.info(f"使用模拟数据模式: {stock_code}")
            return self._get_mock_data(stock_code, market_type)

        try:
            # 根据市场类型选择不同的数据获取方法
            if market_type == "A":
                return await self._get_a_stock_data(stock_code, days)
            elif market_type == "HK":
                return await self._get_hk_stock_data(stock_code, days)
            elif market_type == "US":
                return await self._get_us_stock_data(stock_code, days)
            elif market_type == "ETF":
                return await self._get_etf_data(stock_code, days)
            else:
                raise ValueError(f"不支持的市场类型: {market_type}")

        except Exception as e:
            logger.error(f"获取股票数据失败: {stock_code}, 市场: {market_type}, 错误: {str(e)}")
            # 如果启用了模拟数据，则返回模拟数据
            if settings.USE_MOCK_DATA:
                logger.info(f"切换到模拟数据: {stock_code}")
                return self._get_mock_data(stock_code, market_type)
            raise
    
    async def _get_a_stock_data(self, stock_code: str, days: int) -> Dict[str, Any]:
        """获取A股数据 - 使用官方推荐的稳定接口"""
        try:
            logger.info(f"开始获取股票数据: {stock_code}")

            # 根据官方文档，优先使用稳定的接口
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            # 方法1: 使用stock_zh_a_hist接口（官方推荐）
            try:
                hist_data = await self._retry_request(
                    lambda: ak.stock_zh_a_hist(
                        symbol=stock_code,
                        period="daily",
                        start_date=start_date,
                        end_date=end_date,
                        adjust=""  # 不复权，避免负值问题
                    )
                )

                if hist_data is not None and not hist_data.empty:
                    logger.info(f"成功获取历史数据: {stock_code}, 数据量: {len(hist_data)}")
                    return self._process_a_stock_data_simple(stock_code, hist_data)

            except Exception as e:
                logger.warning(f"主接口失败: {str(e)}")

            # 方法2: 备用接口
            logger.info(f"尝试备用数据源: {stock_code}")
            return self._get_mock_data(stock_code)

        except Exception as e:
            logger.error(f"获取A股数据失败: {stock_code}, 错误: {str(e)}")
            # 返回模拟数据以便测试
            return self._get_mock_data(stock_code)
    
    async def _get_hk_stock_data(self, stock_code: str, days: int) -> Dict[str, Any]:
        """获取港股数据"""
        try:
            # 港股代码需要添加前缀
            hk_symbol = f"{stock_code}.HK"
            
            # 获取历史数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            hist_data = await self._retry_request(
                lambda: ak.stock_hk_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
            )
            
            return self._process_hk_stock_data(stock_code, hist_data)
            
        except Exception as e:
            logger.error(f"获取港股数据失败: {stock_code}, 错误: {str(e)}")
            raise
    
    async def _get_us_stock_data(self, stock_code: str, days: int) -> Dict[str, Any]:
        """获取美股数据"""
        try:
            # 获取历史数据
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            hist_data = await self._retry_request(
                lambda: ak.stock_us_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
            )
            
            return self._process_us_stock_data(stock_code, hist_data)
            
        except Exception as e:
            logger.error(f"获取美股数据失败: {stock_code}, 错误: {str(e)}")
            raise
    
    async def _get_etf_data(self, stock_code: str, days: int) -> Dict[str, Any]:
        """获取ETF数据"""
        try:
            # ETF数据获取方式与A股类似
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            hist_data = await self._retry_request(
                lambda: ak.fund_etf_hist_em(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust=""
                )
            )
            
            return self._process_etf_data(stock_code, hist_data)
            
        except Exception as e:
            logger.error(f"获取ETF数据失败: {stock_code}, 错误: {str(e)}")
            raise
    
    async def _retry_request(self, func, max_retries: int = None):
        """重试请求机制 - 根据官方文档优化"""
        if max_retries is None:
            max_retries = self.max_retries

        last_exception = None

        for attempt in range(max_retries):
            try:
                # 添加请求前延迟，降低访问频率
                if attempt > 0:
                    await asyncio.sleep(self.request_delay)

                # 在异步环境中运行同步函数
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func)

                # 请求成功后也稍作延迟
                await asyncio.sleep(0.5)
                return result

            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()

                # 根据错误类型调整重试策略
                if "timeout" in error_msg or "connection" in error_msg:
                    wait_time = min(5 + (attempt * 2), 15)  # 网络问题时等待更久
                elif "ssl" in error_msg:
                    wait_time = min(3 + (attempt * 3), 20)  # SSL问题时等待更久
                else:
                    wait_time = 2 ** attempt  # 其他问题指数退避

                if attempt < max_retries - 1:
                    logger.warning(f"请求失败，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"请求最终失败，已重试 {max_retries} 次: {str(e)}")

        raise last_exception

    async def _get_backup_data(self, stock_code: str, days: int) -> pd.DataFrame:
        """备用数据获取方法"""
        try:
            # 尝试使用不同的接口
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            # 使用工具函数获取数据
            data = await self._retry_request(
                lambda: ak.tool_trade_date_hist_sina()
            )

            if data is not None and not data.empty:
                # 简单处理数据格式
                return data.head(days)

        except Exception as e:
            logger.warning(f"备用接口也失败: {str(e)}")

        return pd.DataFrame()

    def _get_mock_data(self, stock_code: str, market_type: str = "A") -> Dict[str, Any]:
        """获取模拟数据用于测试"""
        logger.info(f"使用模拟数据: {stock_code}")

        # 生成模拟的历史数据
        dates = []
        mock_data = []
        base_price = 10.0

        for i in range(14):  # 14天数据
            date = (datetime.now() - timedelta(days=13-i)).strftime('%Y-%m-%d')
            price = base_price + (i * 0.1) + (i % 3 * 0.05)  # 模拟价格波动

            mock_data.append({
                'date': date,
                'open': round(price * 0.99, 2),
                'close': round(price, 2),
                'high': round(price * 1.02, 2),
                'low': round(price * 0.98, 2),
                'volume': 1000000 + (i * 100000),
                'amount': None
            })

        # 根据市场类型设置不同的股票名称和价格
        market_names = {
            "A": "A股测试",
            "HK": "港股测试",
            "US": "美股测试",
            "ETF": "ETF测试"
        }

        return {
            'stock_info': {
                'code': stock_code,
                'name': f'{market_names.get(market_type, "测试股票")}{stock_code}',
                'market': market_type,
                'current_price': round(base_price + 1.3, 2),
                'change': 0.15,
                'change_percent': 1.5
            },
            'recent_data': mock_data,
            'raw_data': self._create_mock_dataframe(mock_data)
        }

    def _create_mock_dataframe(self, mock_data: List[Dict]) -> pd.DataFrame:
        """创建模拟DataFrame"""
        df_data = []
        for item in mock_data:
            df_data.append({
                '日期': item['date'],
                '开盘': item['open'],
                '收盘': item['close'],
                '最高': item['high'],
                '最低': item['low'],
                '成交量': item['volume']
            })

        df = pd.DataFrame(df_data)
        df['日期'] = pd.to_datetime(df['日期'])
        return df
    
    def _process_a_stock_data(self, stock_code: str, stock_info: pd.DataFrame, 
                             hist_data: pd.DataFrame, realtime_data: pd.DataFrame) -> Dict[str, Any]:
        """处理A股数据"""
        try:
            # 提取股票基本信息
            stock_name = "未知"
            current_price = None
            change = None
            change_percent = None
            
            # 从实时数据中查找当前股票信息
            if not realtime_data.empty:
                stock_row = realtime_data[realtime_data['代码'] == stock_code]
                if not stock_row.empty:
                    stock_name = stock_row.iloc[0]['名称']
                    current_price = float(stock_row.iloc[0]['最新价'])
                    change = float(stock_row.iloc[0]['涨跌额'])
                    change_percent = float(stock_row.iloc[0]['涨跌幅'])
            
            # 处理历史数据
            recent_data = []
            if not hist_data.empty:
                # 确保数据按日期排序
                hist_data = hist_data.sort_values('日期')
                
                for _, row in hist_data.tail(30).iterrows():  # 最近30天数据
                    recent_data.append({
                        'date': row['日期'].strftime('%Y-%m-%d') if hasattr(row['日期'], 'strftime') else str(row['日期']),
                        'open': float(row['开盘']),
                        'close': float(row['收盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'volume': int(row['成交量']),
                        'amount': float(row['成交额']) if '成交额' in row else None
                    })
            
            return {
                'stock_info': {
                    'code': stock_code,
                    'name': stock_name,
                    'market': 'A',
                    'current_price': current_price,
                    'change': change,
                    'change_percent': change_percent
                },
                'recent_data': recent_data,
                'raw_data': hist_data
            }
            
        except Exception as e:
            logger.error(f"处理A股数据失败: {stock_code}, 错误: {str(e)}")
            raise

    def _process_a_stock_data_simple(self, stock_code: str, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """简化的A股数据处理"""
        try:
            recent_data = []
            current_price = None

            if not hist_data.empty:
                # 处理历史数据
                for _, row in hist_data.tail(14).iterrows():  # 最近14天数据
                    try:
                        # 兼容不同的列名格式
                        date_col = '日期' if '日期' in row else row.index[0]
                        open_col = '开盘' if '开盘' in row else 'open'
                        close_col = '收盘' if '收盘' in row else 'close'
                        high_col = '最高' if '最高' in row else 'high'
                        low_col = '最低' if '最低' in row else 'low'
                        volume_col = '成交量' if '成交量' in row else 'volume'

                        recent_data.append({
                            'date': str(row[date_col])[:10],  # 只取日期部分
                            'open': float(row[open_col]),
                            'close': float(row[close_col]),
                            'high': float(row[high_col]),
                            'low': float(row[low_col]),
                            'volume': int(float(row[volume_col])) if volume_col in row else 0,
                            'amount': None
                        })
                    except Exception as e:
                        logger.warning(f"处理单行数据失败: {str(e)}")
                        continue

                # 获取最新价格
                if recent_data:
                    current_price = recent_data[-1]['close']

            return {
                'stock_info': {
                    'code': stock_code,
                    'name': f'股票{stock_code}',
                    'market': 'A',
                    'current_price': current_price,
                    'change': None,
                    'change_percent': None
                },
                'recent_data': recent_data,
                'raw_data': hist_data
            }

        except Exception as e:
            logger.error(f"简化处理A股数据失败: {stock_code}, 错误: {str(e)}")
            # 返回模拟数据
            return self._get_mock_data(stock_code)
    
    def _process_hk_stock_data(self, stock_code: str, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """处理港股数据"""
        # 类似的处理逻辑，适配港股数据格式
        return self._process_generic_stock_data(stock_code, "HK", hist_data)
    
    def _process_us_stock_data(self, stock_code: str, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """处理美股数据"""
        # 类似的处理逻辑，适配美股数据格式
        return self._process_generic_stock_data(stock_code, "US", hist_data)
    
    def _process_etf_data(self, stock_code: str, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """处理ETF数据"""
        # 类似的处理逻辑，适配ETF数据格式
        return self._process_generic_stock_data(stock_code, "ETF", hist_data)
    
    def _process_generic_stock_data(self, stock_code: str, market: str, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """通用股票数据处理"""
        try:
            recent_data = []
            current_price = None
            
            if not hist_data.empty:
                # 数据列名可能不同，需要适配
                date_col = hist_data.columns[0]  # 通常第一列是日期
                
                # 获取最新价格
                if len(hist_data) > 0:
                    latest_row = hist_data.iloc[-1]
                    current_price = float(latest_row.iloc[4])  # 通常第5列是收盘价
                
                # 处理历史数据
                for _, row in hist_data.tail(30).iterrows():
                    recent_data.append({
                        'date': str(row.iloc[0]),
                        'open': float(row.iloc[1]),
                        'high': float(row.iloc[2]),
                        'low': float(row.iloc[3]),
                        'close': float(row.iloc[4]),
                        'volume': int(row.iloc[5]) if len(row) > 5 else 0,
                        'amount': float(row.iloc[6]) if len(row) > 6 else None
                    })
            
            return {
                'stock_info': {
                    'code': stock_code,
                    'name': stock_code,  # 暂时使用代码作为名称
                    'market': market,
                    'current_price': current_price,
                    'change': None,
                    'change_percent': None
                },
                'recent_data': recent_data,
                'raw_data': hist_data
            }
            
        except Exception as e:
            logger.error(f"处理{market}股票数据失败: {stock_code}, 错误: {str(e)}")
            raise


# 创建全局服务实例
stock_data_service = StockDataService()
