"""
服务器启动脚本
"""
import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings


def main():
    """启动服务器"""
    print("🚀 启动股票分析API服务...")
    print(f"📍 服务地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API文档: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔧 调试模式: {'开启' if settings.DEBUG else '关闭'}")
    print("=" * 50)

    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="debug",
            access_log=True,
            use_colors=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
