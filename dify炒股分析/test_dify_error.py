"""
测试Dify错误请求
模拟Dify发送的错误请求，查看详细的错误信息和日志
"""
import requests
import json
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dify_error_requests():
    """测试Dify发送的错误请求"""
    base_url = "http://10.7.139.26:8001"
    
    print("🔍 测试Dify错误请求...")
    print("=" * 50)
    
    # 1. 测试变量未解析的情况
    print("\n1. 测试变量未解析的情况:")
    try:
        response = requests.post(
            f"{base_url}/analyze-stock-test/",
            json={
                "stock_code": "(+) 变量聚合",
                "market_type": "命令开始"
            },
            timeout=10
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
        if response.status_code == 422:
            print("   ✅ 正确识别了参数验证错误")
        else:
            print("   ❌ 意外的响应状态")
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 2. 测试空值情况
    print("\n2. 测试空值情况:")
    try:
        response = requests.post(
            f"{base_url}/analyze-stock-test/",
            json={
                "stock_code": "",
                "market_type": ""
            },
            timeout=10
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 3. 测试无效的JSON格式
    print("\n3. 测试无效的JSON格式:")
    try:
        response = requests.post(
            f"{base_url}/analyze-stock-test/",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 4. 测试缺少必需字段
    print("\n4. 测试缺少必需字段:")
    try:
        response = requests.post(
            f"{base_url}/analyze-stock-test/",
            json={
                "stock_code": "600132"
                # 缺少 market_type
            },
            timeout=10
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 5. 测试正确的请求（对比）
    print("\n5. 测试正确的请求（对比）:")
    try:
        response = requests.post(
            f"{base_url}/analyze-stock-test/",
            json={
                "stock_code": "600132",
                "market_type": "A"
            },
            timeout=10
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功获取股票: {data['data']['stock_info']['name']}")
        else:
            print(f"   ❌ 失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")

def test_connection_issues():
    """测试连接问题"""
    print("\n🔍 测试连接问题...")
    print("=" * 30)
    
    # 测试错误的端口
    print("\n1. 测试错误的端口:")
    try:
        response = requests.post(
            "http://10.7.139.26:9999/analyze-stock-test/",
            json={"stock_code": "600132", "market_type": "A"},
            timeout=5
        )
        print(f"   意外成功: {response.status_code}")
    except requests.exceptions.ConnectTimeout:
        print("   ✅ 连接超时（预期）")
    except requests.exceptions.ConnectionError:
        print("   ✅ 连接错误（预期）")
    except Exception as e:
        print(f"   ❌ 其他异常: {e}")
    
    # 测试错误的IP
    print("\n2. 测试错误的IP:")
    try:
        response = requests.post(
            "http://192.168.1.999:8001/analyze-stock-test/",
            json={"stock_code": "600132", "market_type": "A"},
            timeout=5
        )
        print(f"   意外成功: {response.status_code}")
    except requests.exceptions.ConnectTimeout:
        print("   ✅ 连接超时（预期）")
    except requests.exceptions.ConnectionError:
        print("   ✅ 连接错误（预期）")
    except Exception as e:
        print(f"   ❌ 其他异常: {e}")

def analyze_dify_issue():
    """分析Dify问题"""
    print("\n📊 Dify问题分析:")
    print("=" * 30)
    
    print("""
根据测试结果，Dify HTTP请求失败的可能原因：

1. 🔴 变量传递问题：
   - JSON中的 "(+) 变量聚合" 和 "命令开始" 不是有效值
   - 这表明Dify工作流中的变量没有正确解析
   
2. 🔴 参数验证失败：
   - market_type 必须是 ['A', 'HK', 'US', 'ETF'] 之一
   - stock_code 必须符合对应市场的格式要求
   
3. 🔴 工作流配置问题：
   - 上游节点可能没有正确输出变量
   - 变量引用语法可能不正确
   
4. ✅ 服务器本身工作正常：
   - API端点可以正常响应
   - 错误处理机制正常工作
   
解决方案：
1. 检查Dify工作流中的变量配置
2. 确保上游节点正确输出 stock_code 和 market_type
3. 验证变量引用语法：{{#节点ID.变量名#}}
4. 可以先用固定值测试，确认API连接正常
    """)

if __name__ == "__main__":
    print("🚀 开始Dify错误请求测试")
    
    # 测试各种错误情况
    test_dify_error_requests()
    
    # 测试连接问题
    test_connection_issues()
    
    # 分析问题
    analyze_dify_issue()
    
    print("\n✅ 测试完成")
