"""
认证相关工具函数
"""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from config import settings


# 创建HTTPBearer安全方案
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    验证API密钥
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        str: 验证通过的API密钥
        
    Raises:
        HTTPException: 认证失败时抛出异常
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证token格式和有效性
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查API密钥是否在有效列表中
    if token not in settings.VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


def get_current_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    获取当前请求的API密钥（用于依赖注入）
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        str: 当前API密钥
    """
    return verify_api_key(credentials)


class AuthenticationError(Exception):
    """认证错误异常"""
    def __init__(self, message: str = "认证失败"):
        self.message = message
        super().__init__(self.message)


def validate_bearer_token(authorization: Optional[str]) -> str:
    """
    验证Bearer Token格式
    
    Args:
        authorization: Authorization头部值
        
    Returns:
        str: 提取的token
        
    Raises:
        AuthenticationError: 格式错误时抛出异常
    """
    if not authorization:
        raise AuthenticationError("缺少Authorization头部")
    
    # 检查Bearer前缀
    if not authorization.lower().startswith("bearer "):
        raise AuthenticationError("Authorization头部格式错误，应为 'Bearer <token>'")
    
    # 提取token
    token = authorization[7:]  # 去掉"Bearer "前缀
    if not token:
        raise AuthenticationError("Token不能为空")
    
    return token


def check_api_key_permissions(api_key: str, required_permissions: list = None) -> bool:
    """
    检查API密钥权限（预留接口，用于未来扩展权限控制）
    
    Args:
        api_key: API密钥
        required_permissions: 所需权限列表
        
    Returns:
        bool: 是否有权限
    """
    # 目前所有有效的API密钥都有完全权限
    # 未来可以根据需要实现更细粒度的权限控制
    return api_key in settings.VALID_API_KEYS
