"""
重试机制处理工具
提供智能重试、错误处理和网络恢复功能
"""
import asyncio
import time
import random
import logging
from functools import wraps
from typing import Callable, Any, Optional, Tuple, List, Union
from enum import Enum
import requests
from requests.exceptions import (
    RequestException, ConnectionError, Timeout, 
    HTTPError, TooManyRedirects, ChunkedEncodingError
)

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """重试策略枚举"""
    FIXED = "fixed"           # 固定间隔
    LINEAR = "linear"         # 线性递增
    EXPONENTIAL = "exponential"  # 指数退避
    RANDOM = "random"         # 随机间隔


class NetworkError(Exception):
    """网络错误基类"""
    pass


class RetryableError(NetworkError):
    """可重试的错误"""
    pass


class NonRetryableError(NetworkError):
    """不可重试的错误"""
    pass


class RetryHandler:
    """智能重试处理器"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        timeout: float = 30.0
    ):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间(秒)
            max_delay: 最大延迟时间(秒)
            strategy: 重试策略
            backoff_factor: 退避因子(用于指数退避)
            jitter: 是否添加随机抖动
            timeout: 请求超时时间
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.timeout = timeout
        
        # 可重试的异常类型
        self.retryable_exceptions = (
            ConnectionError,
            Timeout,
            ChunkedEncodingError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ReadTimeout,
            OSError,  # 网络相关的OS错误
        )
        
        # 可重试的HTTP状态码
        self.retryable_status_codes = {
            408,  # Request Timeout
            429,  # Too Many Requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
            520,  # Unknown Error
            521,  # Web Server Is Down
            522,  # Connection Timed Out
            523,  # Origin Is Unreachable
            524,  # A Timeout Occurred
        }
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        if self.strategy == RetryStrategy.FIXED:
            delay = self.base_delay
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * attempt
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        elif self.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(self.base_delay, self.base_delay * 3)
        else:
            delay = self.base_delay
        
        # 限制最大延迟
        delay = min(delay, self.max_delay)
        
        # 添加随机抖动避免雷群效应
        if self.jitter:
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """判断错误是否可重试"""
        # 检查异常类型
        if isinstance(error, self.retryable_exceptions):
            return True
        
        # 检查HTTP错误状态码
        if isinstance(error, HTTPError):
            if hasattr(error, 'response') and error.response is not None:
                return error.response.status_code in self.retryable_status_codes
        
        # 检查特定错误消息
        error_msg = str(error).lower()
        retryable_keywords = [
            'connection', 'timeout', 'network', 'unreachable',
            'temporary', 'busy', 'overload', 'rate limit'
        ]
        
        return any(keyword in error_msg for keyword in retryable_keywords)
    
    def retry_sync(self, func: Callable) -> Callable:
        """同步函数重试装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, self.max_retries + 2):  # +1 for initial attempt
                try:
                    logger.debug(f"尝试执行 {func.__name__} (第{attempt}次)")
                    result = func(*args, **kwargs)
                    
                    if attempt > 1:
                        logger.info(f"{func.__name__} 在第{attempt}次尝试后成功")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt > self.max_retries + 1:
                        logger.error(f"{func.__name__} 达到最大重试次数({self.max_retries})")
                        break
                    
                    if not self._is_retryable_error(e):
                        logger.error(f"{func.__name__} 遇到不可重试错误: {str(e)}")
                        raise NonRetryableError(f"不可重试错误: {str(e)}") from e
                    
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"{func.__name__} 第{attempt}次尝试失败: {str(e)}, "
                        f"{delay:.2f}秒后重试"
                    )
                    
                    time.sleep(delay)
            
            # 所有重试都失败了
            raise RetryableError(f"重试{self.max_retries}次后仍然失败: {str(last_exception)}") from last_exception
        
        return wrapper
    
    def retry_async(self, func: Callable) -> Callable:
        """异步函数重试装饰器"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, self.max_retries + 2):  # +1 for initial attempt
                try:
                    logger.debug(f"尝试执行 {func.__name__} (第{attempt}次)")
                    result = await func(*args, **kwargs)
                    
                    if attempt > 1:
                        logger.info(f"{func.__name__} 在第{attempt}次尝试后成功")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt > self.max_retries + 1:
                        logger.error(f"{func.__name__} 达到最大重试次数({self.max_retries})")
                        break
                    
                    if not self._is_retryable_error(e):
                        logger.error(f"{func.__name__} 遇到不可重试错误: {str(e)}")
                        raise NonRetryableError(f"不可重试错误: {str(e)}") from e
                    
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"{func.__name__} 第{attempt}次尝试失败: {str(e)}, "
                        f"{delay:.2f}秒后重试"
                    )
                    
                    await asyncio.sleep(delay)
            
            # 所有重试都失败了
            raise RetryableError(f"重试{self.max_retries}次后仍然失败: {str(last_exception)}") from last_exception
        
        return wrapper


# 预定义的重试处理器实例
default_retry_handler = RetryHandler(
    max_retries=3,
    base_delay=1.0,
    strategy=RetryStrategy.EXPONENTIAL,
    backoff_factor=2.0,
    jitter=True,
    timeout=30.0
)

aggressive_retry_handler = RetryHandler(
    max_retries=5,
    base_delay=0.5,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL,
    backoff_factor=1.5,
    jitter=True,
    timeout=45.0
)

gentle_retry_handler = RetryHandler(
    max_retries=2,
    base_delay=2.0,
    strategy=RetryStrategy.LINEAR,
    jitter=False,
    timeout=20.0
)


# 便捷装饰器函数
def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
):
    """便捷的重试装饰器"""
    handler = RetryHandler(
        max_retries=max_retries,
        base_delay=base_delay,
        strategy=strategy
    )
    
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            return handler.retry_async(func)
        else:
            return handler.retry_sync(func)
    
    return decorator


def with_timeout(timeout: float):
    """超时装饰器"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                except asyncio.TimeoutError:
                    raise Timeout(f"函数 {func.__name__} 执行超时 ({timeout}秒)")
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 对于同步函数，我们无法直接实现超时，但可以记录警告
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    logger.warning(f"函数 {func.__name__} 执行时间({elapsed:.2f}s)超过建议超时时间({timeout}s)")
                return result
            return sync_wrapper
    
    return decorator
