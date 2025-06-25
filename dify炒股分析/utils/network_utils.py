"""
网络工具模块
提供健壮的HTTP请求和网络连接功能
"""
import requests
import asyncio
import aiohttp
import time
import logging
from typing import Dict, Any, Optional, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .retry_handler import default_retry_handler, with_timeout, RetryableError

logger = logging.getLogger(__name__)


class NetworkUtils:
    """网络工具类"""
    
    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        """
        初始化网络工具
        
        Args:
            timeout: 请求超时时间
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建配置好的requests会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        # 配置适配器
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置默认headers
        session.headers.update({
            'User-Agent': 'StockAnalysis/1.0 (Python requests)',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        return session
    
    @default_retry_handler.retry_sync
    @with_timeout(30.0)
    def get(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> requests.Response:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            params: 查询参数
            headers: 请求头
            
        Returns:
            requests.Response: 响应对象
        """
        try:
            logger.debug(f"发送GET请求: {url}")
            
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            response = self.session.get(
                url,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            logger.debug(f"GET请求成功: {url} (状态码: {response.status_code})")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GET请求失败: {url} - {str(e)}")
            raise
    
    @default_retry_handler.retry_sync
    @with_timeout(30.0)
    def post(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None, 
             headers: Optional[Dict] = None) -> requests.Response:
        """
        发送POST请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            
        Returns:
            requests.Response: 响应对象
        """
        try:
            logger.debug(f"发送POST请求: {url}")
            
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)
            
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            logger.debug(f"POST请求成功: {url} (状态码: {response.status_code})")
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"POST请求失败: {url} - {str(e)}")
            raise
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()


class AsyncNetworkUtils:
    """异步网络工具类"""
    
    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        """
        初始化异步网络工具

        Args:
            timeout: 请求超时时间
            max_retries: 最大重试次数
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.connector = None  # 延迟初始化，避免事件循环问题

    def _get_connector(self):
        """获取连接器，延迟初始化"""
        if self.connector is None:
            self.connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
        return self.connector
    
    @default_retry_handler.retry_async
    async def get(self, url: str, params: Optional[Dict] = None, 
                  headers: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送异步GET请求
        
        Args:
            url: 请求URL
            params: 查询参数
            headers: 请求头
            
        Returns:
            Dict: 响应数据
        """
        default_headers = {
            'User-Agent': 'StockAnalysis/1.0 (aiohttp)',
            'Accept': 'application/json, text/plain, */*',
        }
        
        if headers:
            default_headers.update(headers)
        
        async with aiohttp.ClientSession(
            connector=self._get_connector(),
            timeout=self.timeout,
            headers=default_headers
        ) as session:
            try:
                logger.debug(f"发送异步GET请求: {url}")
                
                async with session.get(url, params=params) as response:
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 尝试解析JSON
                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:
                        # 如果不是JSON，返回文本
                        data = await response.text()
                    
                    logger.debug(f"异步GET请求成功: {url} (状态码: {response.status})")
                    return {
                        'status_code': response.status,
                        'data': data,
                        'headers': dict(response.headers)
                    }
                    
            except aiohttp.ClientError as e:
                logger.error(f"异步GET请求失败: {url} - {str(e)}")
                raise
    
    @default_retry_handler.retry_async
    async def post(self, url: str, data: Optional[Dict] = None, 
                   json: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送异步POST请求
        
        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头
            
        Returns:
            Dict: 响应数据
        """
        default_headers = {
            'User-Agent': 'StockAnalysis/1.0 (aiohttp)',
            'Accept': 'application/json, text/plain, */*',
        }
        
        if headers:
            default_headers.update(headers)
        
        async with aiohttp.ClientSession(
            connector=self._get_connector(),
            timeout=self.timeout,
            headers=default_headers
        ) as session:
            try:
                logger.debug(f"发送异步POST请求: {url}")
                
                async with session.post(url, data=data, json=json) as response:
                    # 检查响应状态
                    response.raise_for_status()
                    
                    # 尝试解析JSON
                    try:
                        response_data = await response.json()
                    except aiohttp.ContentTypeError:
                        # 如果不是JSON，返回文本
                        response_data = await response.text()
                    
                    logger.debug(f"异步POST请求成功: {url} (状态码: {response.status})")
                    return {
                        'status_code': response.status,
                        'data': response_data,
                        'headers': dict(response.headers)
                    }
                    
            except aiohttp.ClientError as e:
                logger.error(f"异步POST请求失败: {url} - {str(e)}")
                raise
    
    async def close(self):
        """关闭连接器"""
        if self.connector:
            await self.connector.close()


# 全局网络工具实例
network_utils = NetworkUtils()
# 异步网络工具实例将在需要时创建，避免事件循环问题
async_network_utils = None


def get_async_network_utils():
    """获取异步网络工具实例"""
    global async_network_utils
    if async_network_utils is None:
        async_network_utils = AsyncNetworkUtils()
    return async_network_utils


def check_network_connectivity(test_urls: Optional[list] = None) -> bool:
    """
    检查网络连接性
    
    Args:
        test_urls: 测试URL列表
        
    Returns:
        bool: 网络是否可用
    """
    if test_urls is None:
        test_urls = [
            'https://www.baidu.com',
            'https://www.google.com',
            'http://httpbin.org/get'
        ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"网络连接正常: {url}")
                return True
        except Exception as e:
            logger.debug(f"测试URL失败: {url} - {str(e)}")
            continue
    
    logger.warning("网络连接检查失败")
    return False


async def async_check_network_connectivity(test_urls: Optional[list] = None) -> bool:
    """
    异步检查网络连接性
    
    Args:
        test_urls: 测试URL列表
        
    Returns:
        bool: 网络是否可用
    """
    if test_urls is None:
        test_urls = [
            'https://www.baidu.com',
            'https://www.google.com',
            'http://httpbin.org/get'
        ]
    
    timeout = aiohttp.ClientTimeout(total=5)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for url in test_urls:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.info(f"网络连接正常: {url}")
                        return True
            except Exception as e:
                logger.debug(f"测试URL失败: {url} - {str(e)}")
                continue
    
    logger.warning("网络连接检查失败")
    return False
