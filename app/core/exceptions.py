"""
自定义业务异常类
"""


class BaseBusinessException(Exception):
    """业务异常基类"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)


class AuthException(BaseBusinessException):
    """认证异常"""
    pass


class CardException(BaseBusinessException):
    """卡密异常"""
    pass


class PermissionException(BaseBusinessException):
    """权限异常"""
    pass


class UserException(BaseBusinessException):
    """用户异常"""
    pass


class DeviceException(BaseBusinessException):
    """设备异常"""
    pass


class AppException(BaseBusinessException):
    """应用异常"""
    pass


class ValidationException(BaseBusinessException):
    """数据验证异常"""
    pass


class DatabaseException(BaseBusinessException):
    """数据库异常"""
    pass
