#!/usr/bin/env python3
"""
测试Docker容器访问宿主机API的脚本
"""
import requests
import json
import time

def test_docker_access():
    """测试Docker访问宿主机API"""
    
    # 测试不同的URL（Docker环境下）
    test_urls = [
        "http://localhost:8002",           # 容器内localhost（会失败）
        "http://127.0.0.1:8002",          # 容器内127.0.0.1（会失败）
        "http://host.docker.internal:8002", # Docker特殊域名（推荐）
        "http://10.7.139.26:8002",        # 宿主机IP地址
        "http://172.17.0.1:8002",         # Docker默认网关
        "http://172.22.160.1:8002"        # WSL网关
    ]
    
    headers = {
        'Authorization': 'bearer xue1234',
        'Content-Type': 'application/json'
    }
    
    test_data = {
        'stock_code': '600967',
        'market_type': 'A'
    }
    
    print("🐳 测试Docker容器访问宿主机API...")
    print("=" * 60)
    
    for url in test_urls:
        print(f"\n📡 测试URL: {url}")
        
        # 测试健康检查
        try:
            health_url = f"{url}/health"
            response = requests.get(health_url, timeout=5)
            print(f"  ✅ 健康检查: {response.status_code}")
            
            # 如果健康检查成功，测试股票分析API
            analyze_url = f"{url}/analyze-stock/"
            response = requests.post(
                analyze_url, 
                headers=headers, 
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                data = result.get('data', {})
                stock_info = data.get('stock_info', {})
                
                print(f"  ✅ 股票分析: {response.status_code}")
                print(f"     股票: {stock_info.get('name', '未知')}")
                print(f"     价格: {stock_info.get('current_price', '未知')}")
                print(f"  🎯 推荐使用此URL: {url}")
            else:
                print(f"  ⚠️ 股票分析失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 连接失败: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Docker环境下的解决方案:")
    print("1. 优先使用: http://host.docker.internal:8002/analyze-stock/")
    print("2. 备选方案: http://10.7.139.26:8002/analyze-stock/")
    print("3. 如果都不行，可能需要配置Docker网络")
    print("\n📋 Dify配置步骤:")
    print("1. 打开Dify工作流编辑器")
    print("2. 找到HTTP请求节点")
    print("3. 将URL改为上述推荐的地址")
    print("4. 保存并测试工作流")

if __name__ == "__main__":
    test_docker_access()
