"""
启动MCP服务器的脚本
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.server import main

if __name__ == "__main__":
    print("🚀 启动股票分析MCP服务器...")
    print("📝 服务器将通过stdio与Claude Desktop通信")
    print("🔧 请确保在Claude Desktop中正确配置了MCP服务器")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
