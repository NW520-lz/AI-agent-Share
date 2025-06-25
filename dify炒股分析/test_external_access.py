#!/usr/bin/env python3
"""
测试外部访问API的脚本
"""
import requests
import json
import time

def test_api_access():
    """测试API访问"""
    
    # 测试不同的URL
    base_urls = [
        "http://localhost:8002",
        "http://127.0.0.1:8002", 
        "http://10.7.139.26:8002"
    ]
    
    headers = {
        'Authorization': 'bearer xue1234',
        'Content-Type': 'application/json'
    }
    
    test_data = {
        'stock_code': '600967',
        'market_type': 'A'
    }
    
    print("🔄 测试API外部访问...")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\n📡 测试URL: {base_url}")
        
        # 测试健康检查
        try:
            health_url = f"{base_url}/health"
            response = requests.get(health_url, timeout=10)
            print(f"  ✅ 健康检查: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 健康检查失败: {str(e)}")
            continue
            
        # 测试股票分析API
        try:
            analyze_url = f"{base_url}/analyze-stock/"
            response = requests.post(
                analyze_url, 
                headers=headers, 
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                stock_info = data.get('stock_info', {})
                recent_data = data.get('recent_data', [])
                
                print(f"  ✅ 股票分析: {response.status_code}")
                print(f"     股票: {stock_info.get('name', '未知')}")
                print(f"     价格: {stock_info.get('current_price', '未知')}")
                print(f"     数据: {len(recent_data)}条")
            else:
                print(f"  ❌ 股票分析失败: {response.status_code}")
                print(f"     错误: {response.text}")
                
        except Exception as e:
            print(f"  ❌ 股票分析异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 建议:")
    print("1. 如果localhost和127.0.0.1都正常，但10.7.139.26失败，可能是防火墙问题")
    print("2. 在Dify中使用: http://10.7.139.26:8002/analyze-stock/")
    print("3. 如果仍然失败，请检查Dify是否运行在Docker容器中")

if __name__ == "__main__":
    test_api_access()
