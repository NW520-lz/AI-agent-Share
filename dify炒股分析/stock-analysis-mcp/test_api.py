"""
测试HTTP API接口
"""

import requests
import json
import time

def test_api():
    """测试API接口"""
    base_url = "http://10.7.139.26:8003"
    
    print("🔍 测试股票分析HTTP API...")
    print("=" * 50)
    
    # 1. 测试健康检查
    print("1. 测试健康检查:")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        print("   ✅ 健康检查通过")
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
        return
    
    print("\n" + "=" * 50)
    
    # 2. 测试股票基本信息
    print("2. 测试股票基本信息 (600132):")
    try:
        payload = {
            "stock_code": "600132",
            "market_type": "A"
        }
        response = requests.post(
            f"{base_url}/stock-info", 
            json=payload, 
            timeout=30
        )
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                stock_info = data['data']['stock_info']
                print(f"   股票名称: {stock_info['name']}")
                print(f"   当前价格: {stock_info['current_price']}")
                print("   ✅ 股票信息获取成功")
            else:
                print(f"   ❌ API返回错误: {data.get('error')}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n" + "=" * 50)
    
    # 3. 测试市场状态
    print("3. 测试市场状态:")
    try:
        response = requests.get(f"{base_url}/market-status", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                market_status = data['data']['market_status']
                print(f"   市场状态: {market_status['market_status']}")
                print(f"   当前时间: {market_status['current_time']}")
                print("   ✅ 市场状态获取成功")
            else:
                print(f"   ❌ API返回错误: {data.get('error')}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n" + "=" * 50)
    
    # 4. 测试综合分析（这个可能需要较长时间）
    print("4. 测试综合股票分析 (600132):")
    print("   ⏳ 正在获取数据和分析，请稍候...")
    
    try:
        payload = {
            "stock_code": "600132",
            "market_type": "A",
            "period": "30"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/analyze-stock", 
            json=payload, 
            timeout=120  # 增加超时时间
        )
        end_time = time.time()
        
        print(f"   状态码: {response.status_code}")
        print(f"   耗时: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                analysis_data = data['data']
                stock_info = analysis_data['stock_info']
                technical = analysis_data['technical_summary']
                
                print(f"   股票名称: {stock_info['name']}")
                print(f"   当前价格: {stock_info['current_price']}")
                print(f"   趋势: {technical['trend']}")
                print(f"   RSI: {technical['rsi']}")
                print("   ✅ 综合分析成功")
                
                # 保存完整响应到文件
                with open('api_response_sample.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print("   📄 完整响应已保存到 api_response_sample.json")
                
            else:
                print(f"   ❌ API返回错误: {data.get('error')}")
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ 请求超时，这可能是因为数据获取需要较长时间")
        print("   💡 建议: 在Dify中设置更长的超时时间（60-120秒）")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API测试完成！")
    print("\n📝 Dify配置建议:")
    print("   - HTTP请求超时设置: 60-120秒")
    print("   - URL: http://10.7.139.26:8003/analyze-stock")
    print("   - 方法: POST")
    print("   - Content-Type: application/json")
    print("   - 请求体: {\"stock_code\": \"{{#stock_code#}}\", \"market_type\": \"A\", \"period\": \"30\"}")

if __name__ == "__main__":
    test_api()
