"""
API测试脚本
"""
import requests
import json
import time
from typing import Dict, Any


class StockAnalysisAPITester:
    """股票分析API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8002", api_key: str = "xue1234"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def test_health_check(self) -> bool:
        """测试健康检查接口"""
        print("🔍 测试健康检查接口...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过: {data}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {str(e)}")
            return False
    
    def test_analyze_stock(self, stock_code: str, market_type: str) -> bool:
        """测试股票分析接口"""
        print(f"🔍 测试股票分析接口: {stock_code} ({market_type})")
        try:
            payload = {
                "stock_code": stock_code,
                "market_type": market_type
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/analyze-stock/",
                headers=self.headers,
                json=payload
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"⏱️ 响应时间: {response_time:.2f}秒")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 股票分析成功")
                
                # 验证响应数据结构
                if self._validate_stock_analysis_response(data):
                    print("✅ 响应数据结构验证通过")
                    return True
                else:
                    print("❌ 响应数据结构验证失败")
                    return False
            else:
                print(f"❌ 股票分析失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 股票分析异常: {str(e)}")
            return False
    
    def test_market_overview(self, market_type: str = "A") -> bool:
        """测试市场概览接口"""
        print(f"🔍 测试市场概览接口: {market_type}")
        try:
            response = requests.get(
                f"{self.base_url}/market-overview/?market_type={market_type}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 市场概览获取成功")
                return True
            else:
                print(f"❌ 市场概览失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 市场概览异常: {str(e)}")
            return False
    
    def test_authentication(self) -> bool:
        """测试认证机制"""
        print("🔍 测试认证机制...")
        
        # 测试无认证头
        try:
            response = requests.post(
                f"{self.base_url}/analyze-stock/",
                json={"stock_code": "000001", "market_type": "A"}
            )
            if response.status_code == 401:
                print("✅ 无认证头正确拒绝")
            else:
                print(f"❌ 无认证头应该返回401，实际返回: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 测试无认证头异常: {str(e)}")
            return False
        
        # 测试错误的API密钥
        try:
            wrong_headers = {
                "Authorization": "bearer wrong_key",
                "Content-Type": "application/json"
            }
            response = requests.post(
                f"{self.base_url}/analyze-stock/",
                headers=wrong_headers,
                json={"stock_code": "000001", "market_type": "A"}
            )
            if response.status_code == 401:
                print("✅ 错误API密钥正确拒绝")
                return True
            else:
                print(f"❌ 错误API密钥应该返回401，实际返回: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 测试错误API密钥异常: {str(e)}")
            return False
    
    def test_invalid_requests(self) -> bool:
        """测试无效请求"""
        print("🔍 测试无效请求...")
        
        # 测试无效股票代码
        invalid_requests = [
            {"stock_code": "invalid", "market_type": "A"},
            {"stock_code": "000001", "market_type": "INVALID"},
            {"stock_code": "", "market_type": "A"},
        ]
        
        for req in invalid_requests:
            try:
                response = requests.post(
                    f"{self.base_url}/analyze-stock/",
                    headers=self.headers,
                    json=req
                )
                if response.status_code == 422:  # Validation error
                    print(f"✅ 无效请求正确拒绝: {req}")
                else:
                    print(f"❌ 无效请求应该返回422，实际返回: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ 测试无效请求异常: {str(e)}")
                return False
        
        return True
    
    def _validate_stock_analysis_response(self, data: Dict[str, Any]) -> bool:
        """验证股票分析响应数据结构"""
        required_fields = ["status", "data", "timestamp"]
        
        for field in required_fields:
            if field not in data:
                print(f"❌ 缺少必需字段: {field}")
                return False
        
        if data["status"] != "success":
            print(f"❌ 状态不是success: {data['status']}")
            return False
        
        # 验证data字段结构
        data_obj = data["data"]
        required_data_fields = ["stock_info", "technical_summary", "recent_data", "report"]
        
        for field in required_data_fields:
            if field not in data_obj:
                print(f"❌ data中缺少必需字段: {field}")
                return False
        
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始运行API测试套件...")
        print("=" * 50)
        
        test_results = []
        
        # 1. 健康检查测试
        test_results.append(("健康检查", self.test_health_check()))
        
        # 2. 认证测试
        test_results.append(("认证机制", self.test_authentication()))
        
        # 3. 无效请求测试
        test_results.append(("无效请求", self.test_invalid_requests()))
        
        # 4. 股票分析测试
        test_stocks = [
            ("000001", "A"),  # 平安银行
            ("000333", "A"),  # 美的集团
        ]
        
        for stock_code, market_type in test_stocks:
            test_name = f"股票分析-{stock_code}"
            test_results.append((test_name, self.test_analyze_stock(stock_code, market_type)))
        
        # 5. 市场概览测试
        test_results.append(("市场概览", self.test_market_overview()))
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        print("=" * 50)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print("=" * 50)
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有测试通过！")
        else:
            print("⚠️ 部分测试失败，请检查服务状态")


def main():
    """主函数"""
    print("股票分析API测试工具")
    print("请确保API服务已启动在 http://localhost:8000")
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    # 创建测试器并运行测试
    tester = StockAnalysisAPITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
