#!/usr/bin/env python3
"""
模拟Dify HTTP请求的测试脚本
"""
import requests
import json

def test_dify_request():
    """模拟Dify的HTTP请求"""
    
    # 推荐的URL
    url = "http://10.7.139.26:8002/analyze-stock/"
    
    # Dify HTTP请求节点的配置
    headers = {
        "Authorization": "bearer xue1234",
        "Content-Type": "application/json"
    }
    
    # 测试不同的股票代码
    test_stocks = ["600967", "000001", "600132", "000002"]
    
    print("🔄 模拟Dify HTTP请求测试...")
    print("=" * 50)
    print(f"📡 URL: {url}")
    print(f"🔑 Headers: {headers}")
    print("=" * 50)
    
    for stock_code in test_stocks:
        print(f"\n📊 测试股票: {stock_code}")
        
        # 模拟Dify变量替换后的请求体
        request_body = {
            "stock_code": stock_code,
            "market_type": "A"
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=request_body,
                timeout=30
            )
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查响应结构
                if result.get("status") == "success":
                    data = result.get("data", {})
                    stock_info = data.get("stock_info", {})
                    recent_data = data.get("recent_data", [])
                    report = data.get("report", {})
                    technical_summary = data.get("technical_summary", {})

                    print(f"  ✅ 请求成功")
                    print(f"     股票名称: {stock_info.get('name', '未知')}")
                    print(f"     当前价格: {stock_info.get('current_price', '未知')}")
                    print(f"     历史数据: {len(recent_data)}条")
                    print(f"     趋势分析: {technical_summary.get('trend', '未知')}")
                    print(f"     交易建议: {report.get('trading_suggestion', '未知')[:50]}...")

                    # 检查关键字段是否存在
                    required_fields = ['stock_info', 'recent_data', 'report', 'technical_summary']
                    missing_fields = [field for field in required_fields if field not in data]

                    if missing_fields:
                        print(f"  ⚠️ 缺少字段: {missing_fields}")
                    else:
                        print(f"  ✅ 数据完整")

                else:
                    print(f"  ❌ 业务失败: {result.get('message', '未知错误')}")
                    
            else:
                print(f"  ❌ HTTP错误: {response.status_code}")
                print(f"     错误信息: {response.text}")
                
        except Exception as e:
            print(f"  ❌ 请求异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Dify配置建议:")
    print("1. HTTP请求节点URL: http://10.7.139.26:8002/analyze-stock/")
    print("2. 请求方法: POST")
    print("3. Headers:")
    print("   - Authorization: bearer xue1234")
    print("   - Content-Type: application/json")
    print("4. Body (JSON):")
    print('   {"stock_code": "{{#变量聚合器.output#}}", "market_type": "A"}')
    print("\n✅ 如果上述测试都成功，说明API完全正常，问题在于Dify的网络配置")

if __name__ == "__main__":
    test_dify_request()
