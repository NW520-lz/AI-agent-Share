"""
缓存相关工具函数
"""
import json
import hashlib
from typing import Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SimpleCache:
    """简单的内存缓存实现"""
    
    def __init__(self):
        self._cache = {}
        self._expire_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            if key in self._cache:
                # 检查是否过期
                if key in self._expire_times:
                    if datetime.now() > self._expire_times[key]:
                        # 已过期，删除缓存
                        del self._cache[key]
                        del self._expire_times[key]
                        return None
                
                return self._cache[key]
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {key}, 错误: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        """设置缓存值"""
        try:
            self._cache[key] = value
            self._expire_times[key] = datetime.now() + timedelta(seconds=expire_seconds)
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {key}, 错误: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._expire_times:
                del self._expire_times[key]
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {key}, 错误: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            self._cache.clear()
            self._expire_times.clear()
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            return False
    
    def cleanup_expired(self):
        """清理过期缓存"""
        try:
            now = datetime.now()
            expired_keys = []
            
            for key, expire_time in self._expire_times.items():
                if now > expire_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.delete(key)
                
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")
            
        except Exception as e:
            logger.error(f"清理过期缓存失败: {str(e)}")


def generate_cache_key(prefix: str, **kwargs) -> str:
    """
    生成缓存键
    
    Args:
        prefix: 缓存键前缀
        **kwargs: 用于生成键的参数
        
    Returns:
        str: 生成的缓存键
    """
    try:
        # 将参数排序并序列化
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        
        # 生成MD5哈希
        hash_obj = hashlib.md5(params_str.encode('utf-8'))
        hash_str = hash_obj.hexdigest()
        
        return f"{prefix}:{hash_str}"
        
    except Exception as e:
        logger.error(f"生成缓存键失败: {str(e)}")
        return f"{prefix}:default"


# 创建全局缓存实例
cache = SimpleCache()
