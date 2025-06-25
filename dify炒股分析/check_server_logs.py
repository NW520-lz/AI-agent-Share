"""
检查服务器日志和状态
"""
import requests
import json
import time
import logging
from datetime import datetime

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/client_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def check_server_status():
    """检查服务器状态"""
    logger.info("🔍 检查服务器状态...")
    
    try:
        # 健康检查
        response = requests.get("http://10.7.139.26:8001/health", timeout=5)
        logger.info(f"健康检查状态码: {response.status_code}")
        logger.info(f"健康检查响应: {response.json()}")
        
        if response.status_code == 200:
            logger.info("✅ 服务器运行正常")
            return True
        else:
            logger.error("❌ 服务器健康检查失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 服务器连接失败: {str(e)}")
        return False

def simulate_dify_request():
    """模拟Dify的错误请求"""
    logger.info("🔍 模拟Dify的错误请求...")
    
    # 模拟Dify发送的错误数据
    error_data = {
        "stock_code": "(+) 变量聚合",
        "market_type": "命令开始"
    }
    
    try:
        logger.info(f"发送请求数据: {json.dumps(error_data, ensure_ascii=False)}")
        
        response = requests.post(
            "http://10.7.139.26:8001/analyze-stock-test/",
            json=error_data,
            timeout=10
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应头: {dict(response.headers)}")
        logger.info(f"响应内容: {response.text}")
        
        if response.status_code == 422:
            logger.info("✅ 正确返回参数验证错误")
            
            # 解析错误详情
            error_detail = response.json()
            logger.info("错误详情分析:")
            for error in error_detail.get('detail', []):
                logger.info(f"  - 位置: {error.get('loc')}")
                logger.info(f"  - 类型: {error.get('type')}")
                logger.info(f"  - 消息: {error.get('msg')}")
                logger.info(f"  - 输入: {error.get('input')}")
        else:
            logger.warning(f"⚠️ 意外的状态码: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ 请求异常: {str(e)}")

def test_correct_request():
    """测试正确的请求"""
    logger.info("🔍 测试正确的请求...")
    
    correct_data = {
        "stock_code": "600132",
        "market_type": "A"
    }
    
    try:
        logger.info(f"发送正确请求数据: {json.dumps(correct_data, ensure_ascii=False)}")
        
        start_time = time.time()
        response = requests.post(
            "http://10.7.139.26:8001/analyze-stock-test/",
            json=correct_data,
            timeout=30
        )
        end_time = time.time()
        
        logger.info(f"响应时间: {end_time - start_time:.2f}秒")
        logger.info(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ 请求成功")
            logger.info(f"股票名称: {data['data']['stock_info']['name']}")
            logger.info(f"当前价格: {data['data']['stock_info']['current_price']}")
            logger.info(f"技术指标: RSI={data['data']['technical_summary']['rsi']:.2f}")
        else:
            logger.error(f"❌ 请求失败: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ 请求异常: {str(e)}")

def analyze_dify_configuration():
    """分析Dify配置问题"""
    logger.info("📊 分析Dify配置问题...")
    
    print("""
=== Dify HTTP请求失败原因分析 ===

根据日志分析，问题出现在以下几个方面：

1. 🔴 变量解析问题：
   - Dify工作流中的变量 "(+) 变量聚合" 没有被正确解析
   - "命令开始" 不是有效的市场类型值
   
2. 🔴 变量传递链路问题：
   - 上游节点可能没有正确输出变量
   - 变量名称可能不匹配
   - 变量引用语法可能错误

3. ✅ API服务器工作正常：
   - 能够正确处理有效请求
   - 错误处理和验证机制正常
   - 响应时间在可接受范围内

=== 解决方案 ===

1. 检查Dify工作流配置：
   - 确认上游节点正确输出了 stock_code 和 market_type 变量
   - 检查变量引用语法：{{#节点ID.变量名#}}
   - 验证变量数据类型和格式

2. 临时测试方案：
   - 在HTTP请求节点中使用固定值进行测试
   - 例如：{"stock_code": "600132", "market_type": "A"}

3. 调试步骤：
   - 在HTTP请求节点前添加调试节点，查看变量值
   - 逐步检查每个节点的输出
   - 确认变量传递链路完整

4. 常见的Dify变量引用问题：
   - 节点ID不正确
   - 变量名称拼写错误
   - 变量作用域问题
   - 数据类型转换问题
    """)

def main():
    """主函数"""
    logger.info(f"🚀 开始服务器日志检查 - {datetime.now()}")
    
    # 1. 检查服务器状态
    if not check_server_status():
        logger.error("服务器不可用，退出检查")
        return
    
    # 2. 模拟Dify错误请求
    simulate_dify_request()
    
    # 3. 测试正确请求
    test_correct_request()
    
    # 4. 分析配置问题
    analyze_dify_configuration()
    
    logger.info("✅ 日志检查完成")

if __name__ == "__main__":
    main()
