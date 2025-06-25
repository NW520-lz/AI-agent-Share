"""
简单的重试机制测试
"""
import requests
import time
import logging
from utils.retry_handler import retry, RetryableError
from utils.network_utils import check_network_connectivity

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_network_check():
    """测试网络检查"""
    logger.info("=== 测试网络连接检查 ===")
    
    start_time = time.time()
    is_connected = check_network_connectivity()
    elapsed = time.time() - start_time
    
    if is_connected:
        logger.info(f"✅ 网络连接正常 (耗时: {elapsed:.2f}秒)")
    else:
        logger.warning(f"❌ 网络连接异常 (耗时: {elapsed:.2f}秒)")
    
    return is_connected


@retry(max_retries=3, base_delay=1.0)
def test_api_request():
    """测试API请求重试"""
    logger.info("发送API请求...")
    
    try:
        response = requests.post(
            'http://10.7.139.26:8001/analyze-stock-test/',
            json={'stock_code': '600312', 'market_type': 'A'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ API请求成功: {data['data']['stock_info']['name']}")
            return data
        else:
            raise RetryableError(f"HTTP错误: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"请求异常: {str(e)}")
        raise RetryableError(f"请求失败: {str(e)}")


def test_retry_with_different_errors():
    """测试不同类型错误的重试"""
    logger.info("=== 测试不同错误类型的重试 ===")
    
    @retry(max_retries=2, base_delay=0.5)
    def simulate_network_error():
        import random
        error_types = [
            "Connection timeout",
            "Network unreachable",
            "Connection refused"
        ]
        
        if random.random() < 0.8:  # 80%概率失败
            error = random.choice(error_types)
            raise RetryableError(error)
        
        return "成功"
    
    try:
        result = simulate_network_error()
        logger.info(f"✅ 模拟重试成功: {result}")
    except Exception as e:
        logger.error(f"❌ 模拟重试失败: {str(e)}")


def test_api_with_retry():
    """测试带重试的API调用"""
    logger.info("=== 测试API重试机制 ===")
    
    try:
        result = test_api_request()
        
        # 检查技术指标
        technical = result['data']['technical_summary']
        logger.info("技术指标检查:")
        logger.info(f"  MACD: {technical.get('macd', 'None')}")
        logger.info(f"  KDJ_K: {technical.get('kdj_k', 'None')}")
        logger.info(f"  RSI: {technical.get('rsi', 'None')}")
        logger.info(f"  布林带上轨: {technical.get('bollinger_upper', 'None')}")
        
        # 验证修复效果
        indicators_fixed = 0
        if technical.get('kdj_k') is not None:
            indicators_fixed += 1
        if technical.get('rsi') is not None:
            indicators_fixed += 1
        if technical.get('bollinger_upper') is not None:
            indicators_fixed += 1
            
        logger.info(f"✅ 技术指标修复状态: {indicators_fixed}/3 个指标正常")
        
    except Exception as e:
        logger.error(f"❌ API测试失败: {str(e)}")


def main():
    """主测试函数"""
    logger.info("🚀 开始重试机制测试")
    
    # 1. 网络连接测试
    network_ok = test_network_check()
    
    if not network_ok:
        logger.warning("⚠️ 网络连接异常，跳过API测试")
        return
    
    # 2. 重试功能测试
    test_retry_with_different_errors()
    
    # 3. API重试测试
    test_api_with_retry()
    
    logger.info("✅ 测试完成")


if __name__ == "__main__":
    main()
