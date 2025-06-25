"""
简单的API测试
"""
import requests
import json

def test_health():
    """测试健康检查"""
    try:
        response = requests.get("http://localhost:8002/health")
        print(f"健康检查状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_stock_analysis():
    """测试股票分析"""
    try:
        headers = {
            "Authorization": "bearer xue1234",
            "Content-Type": "application/json"
        }
        
        data = {
            "stock_code": "000001",
            "market_type": "A"
        }
        
        print("发送股票分析请求...")
        response = requests.post(
            "http://localhost:8002/analyze-stock/",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"股票分析状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 股票分析成功!")
            print(f"股票信息: {result['data']['stock_info']}")
            return True
        else:
            print(f"❌ 股票分析失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"股票分析异常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始简单API测试...")
    
    # 测试健康检查
    if test_health():
        print("✅ 健康检查通过")
    else:
        print("❌ 健康检查失败")
        exit(1)
    
    # 测试股票分析
    if test_stock_analysis():
        print("✅ 股票分析测试通过")
    else:
        print("❌ 股票分析测试失败")
    
    print("🎉 测试完成!")
