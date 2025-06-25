"""
测试重试机制
验证网络错误处理和重试功能
"""
import asyncio
import logging
import time
from services.stock_data_service import StockDataService
from utils.retry_handler import retry, RetryableError, NonRetryableError
from utils.network_utils import check_network_connectivity, async_check_network_connectivity

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_stock_data_service():
    """测试股票数据服务的重试机制"""
    logger.info("=== 测试股票数据服务重试机制 ===")
    
    service = StockDataService()
    
    # 测试正常情况
    try:
        logger.info("测试正常股票数据获取...")
        result = await service.get_stock_data("600312", "A")
        logger.info(f"✅ 正常获取成功: {result['stock_info']['name']}")
    except Exception as e:
        logger.error(f"❌ 正常获取失败: {str(e)}")
    
    # 测试无效股票代码（不可重试错误）
    try:
        logger.info("测试无效股票代码...")
        result = await service.get_stock_data("999999", "A")
        logger.info("⚠️ 意外成功获取了无效代码的数据")
    except NonRetryableError as e:
        logger.info(f"✅ 正确识别不可重试错误: {str(e)}")
    except Exception as e:
        logger.warning(f"⚠️ 其他错误: {str(e)}")


def test_network_connectivity():
    """测试网络连接检查"""
    logger.info("=== 测试网络连接检查 ===")
    
    # 测试正常网络检查
    start_time = time.time()
    is_connected = check_network_connectivity()
    elapsed = time.time() - start_time
    
    if is_connected:
        logger.info(f"✅ 网络连接正常 (耗时: {elapsed:.2f}秒)")
    else:
        logger.warning(f"❌ 网络连接异常 (耗时: {elapsed:.2f}秒)")
    
    # 测试自定义URL
    custom_urls = [
        'https://www.baidu.com',
        'http://quote.eastmoney.com',
        'https://httpbin.org/get'
    ]
    
    start_time = time.time()
    is_connected = check_network_connectivity(custom_urls)
    elapsed = time.time() - start_time
    
    if is_connected:
        logger.info(f"✅ 自定义URL网络检查正常 (耗时: {elapsed:.2f}秒)")
    else:
        logger.warning(f"❌ 自定义URL网络检查异常 (耗时: {elapsed:.2f}秒)")


async def test_async_network_connectivity():
    """测试异步网络连接检查"""
    logger.info("=== 测试异步网络连接检查 ===")
    
    start_time = time.time()
    is_connected = await async_check_network_connectivity()
    elapsed = time.time() - start_time
    
    if is_connected:
        logger.info(f"✅ 异步网络连接正常 (耗时: {elapsed:.2f}秒)")
    else:
        logger.warning(f"❌ 异步网络连接异常 (耗时: {elapsed:.2f}秒)")


@retry(max_retries=3, base_delay=0.5)
def test_retry_decorator():
    """测试重试装饰器"""
    import random
    
    # 模拟随机失败
    if random.random() < 0.7:  # 70%概率失败
        raise RetryableError("模拟网络错误")
    
    return "成功执行"


async def test_retry_functionality():
    """测试重试功能"""
    logger.info("=== 测试重试装饰器 ===")
    
    try:
        result = test_retry_decorator()
        logger.info(f"✅ 重试成功: {result}")
    except Exception as e:
        logger.error(f"❌ 重试最终失败: {str(e)}")


def simulate_network_issues():
    """模拟网络问题"""
    logger.info("=== 模拟网络问题测试 ===")
    
    # 模拟不同类型的网络错误
    error_types = [
        "Connection timeout",
        "Network unreachable", 
        "SSL handshake failed",
        "DNS resolution failed",
        "Connection refused"
    ]
    
    for error_msg in error_types:
        try:
            raise RetryableError(error_msg)
        except RetryableError as e:
            logger.info(f"✅ 可重试错误: {str(e)}")
        except Exception as e:
            logger.error(f"❌ 意外错误类型: {str(e)}")


async def performance_test():
    """性能测试"""
    logger.info("=== 性能测试 ===")
    
    service = StockDataService()
    
    # 测试多个股票的并发获取
    stock_codes = ["600312", "000001", "000002"]
    
    start_time = time.time()
    
    tasks = []
    for code in stock_codes:
        task = service.get_stock_data(code, "A")
        tasks.append(task)
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"✅ 并发测试完成: {success_count}/{len(stock_codes)} 成功 (耗时: {elapsed:.2f}秒)")
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"  {stock_codes[i]}: 失败 - {str(result)}")
            else:
                logger.info(f"  {stock_codes[i]}: 成功 - {result['stock_info']['name']}")
                
    except Exception as e:
        logger.error(f"❌ 并发测试失败: {str(e)}")


async def main():
    """主测试函数"""
    logger.info("🚀 开始重试机制测试")
    
    # 基础功能测试
    test_network_connectivity()
    await test_async_network_connectivity()
    
    # 重试功能测试
    await test_retry_functionality()
    
    # 模拟网络问题
    simulate_network_issues()
    
    # 股票数据服务测试
    await test_stock_data_service()
    
    # 性能测试
    await performance_test()
    
    logger.info("✅ 所有测试完成")


if __name__ == "__main__":
    asyncio.run(main())
