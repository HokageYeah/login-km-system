from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import ResponseValidationError
from app.schemas.common_data import ApiResponseData, PlatformEnum
from app.core.config import settings
from app.core.exceptions import (
    AuthException, CardException, PermissionException,
    UserException, DeviceException, AppException,
    ValidationException, DatabaseException
)
import httpx
from datetime import datetime, timedelta
from loguru import logger

# 常见请求字段中文名映射。
# 这里放在全局异常处理层，是为了让所有接口的参数校验错误都能复用同一套中文提示，
# 避免只在某一个接口里单点写死提示文案。
FIELD_CN_NAME_MAP = {
    "username": "用户名",
    "password": "密码",
    "app_key": "应用标识",
    "device_id": "设备标识",
    "card_key": "卡密",
    "card_id": "卡密ID",
    "permission": "权限标识",
    "permissions": "权限列表",
    "page": "页码",
    "size": "每页数量",
}

# 创建一个简单的内存锁，用于防止重复调用n8n
n8n_workflow_lock = {
    "is_running": False,
    "started_at": None,
    "max_duration": 300  # 锁定最长时间，单位秒，防止锁死
}
platform_mapping = {
    "wx/public": PlatformEnum.WX_PUBLIC,
    "license": PlatformEnum.LICENSE,
    "wx/public/system": PlatformEnum.SYSTEM,
    "auth": PlatformEnum.LICENSE,
    "card": PlatformEnum.LICENSE,
    "app": PlatformEnum.LICENSE,
    "permission": PlatformEnum.LICENSE,
    "admin": PlatformEnum.LICENSE,
    "admin/feature-permissions": PlatformEnum.LICENSE,
}


def _get_platform(path: str) -> PlatformEnum:
    """根据请求路径获取统一响应平台标识。"""
    return next((v for k, v in platform_mapping.items() if k in path), PlatformEnum.UNKNOWN)


def _get_field_cn_name(field_name: str) -> str:
    """获取字段中文名；没有配置映射时保留原始字段名，便于排查。"""
    return FIELD_CN_NAME_MAP.get(field_name, field_name)


def _format_validation_location(error: dict) -> tuple[str, str, str]:
    """
    将 Pydantic 的 loc 转换为统一的中文位置描述。

    Returns:
        (参数来源, 字段路径, 中文位置描述)
    """
    loc = error.get("loc") or ()
    source = str(loc[0]) if loc else "unknown"

    if source == "query":
        field_path = ".".join(str(item) for item in loc[1:]) if len(loc) > 1 else ""
        return source, field_path, f"查询参数:{field_path or '未知字段'}"

    if source == "body":
        field_path = ".".join(str(item) for item in loc[1:]) if len(loc) > 1 else ""
        return source, field_path, f"请求体:{field_path or '请求体'}"

    if source == "path":
        field_path = ".".join(str(item) for item in loc[1:]) if len(loc) > 1 else ""
        return source, field_path, f"路径参数:{field_path or '未知字段'}"

    if source == "header":
        field_path = ".".join(str(item) for item in loc[1:]) if len(loc) > 1 else ""
        return source, field_path, f"请求头:{field_path or '未知字段'}"

    field_path = ".".join(str(item) for item in loc) if loc else "unknown"
    return source, field_path, field_path


def _translate_validation_error(error: dict) -> str:
    """
    将 Pydantic 原始错误翻译为面向调用方的中文提示。
    不同接口共享这套规则，后续新增 Schema 校验时无需在接口层重复处理。
    """
    _, field_path, location_text = _format_validation_location(error)
    field_name = field_path.split(".")[-1] if field_path else ""
    field_cn_name = _get_field_cn_name(field_name)
    error_type = error.get("type", "")
    ctx = error.get("ctx") or {}

    if error_type == "missing":
        return f"{location_text}，{field_cn_name}不能为空"

    if error_type == "string_too_short":
        min_length = ctx.get("min_length")
        if min_length is not None:
            return f"{location_text}，{field_cn_name}长度不能少于 {min_length} 个字符"
        return f"{location_text}，{field_cn_name}长度过短"

    if error_type == "string_too_long":
        max_length = ctx.get("max_length")
        if max_length is not None:
            return f"{location_text}，{field_cn_name}长度不能超过 {max_length} 个字符"
        return f"{location_text}，{field_cn_name}长度过长"

    if error_type == "value_error":
        raw_message = str(error.get("msg", "参数值不合法"))
        # Pydantic 对 ValueError 会生成类似 "Value error, xxx" 的文案，这里裁剪为更自然的中文提示。
        message = raw_message.replace("Value error, ", "", 1)
        return f"{location_text}，{message}"

    if error_type.endswith("_type"):
        return f"{location_text}，{field_cn_name}类型不正确"

    return f"{location_text}，{error.get('msg', '参数格式错误')}"


def _build_validation_error_detail(error: dict) -> dict:
    """构建结构化校验错误详情，方便日志和接口调用方定位具体字段。"""
    source, field_path, location_text = _format_validation_location(error)
    return {
        "source": source,
        "field": field_path,
        "location": location_text,
        "type": error.get("type"),
        "message": _translate_validation_error(error),
    }


def _build_error_content(request: Request, message: str, data: dict | None = None):
    """
    构建统一错误响应，避免业务异常被响应中间件二次包装成成功响应。
    """
    path = request.url.path
    return {
        "platform": _get_platform(path),
        "ret": [f"ERROR::{message}"],
        "data": data or {},
        "v": settings.VERSION,
        "api": path.strip("/")
    }


def _business_error_response(
    request: Request,
    exc: BaseException,
    status_code: int,
    default_message: str | None = None
):
    """统一业务异常响应格式。"""
    message = getattr(exc, "message", None) or default_message or str(exc)
    code = getattr(exc, "code", exc.__class__.__name__)
    return JSONResponse(
        status_code=status_code,
        content=_build_error_content(
            request=request,
            message=message,
            data={"code": code}
        )
    )


# 自定义HTTP异常处理器
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    统一处理HTTP异常，转换为指定格式
    """
    print('http_exception_handler----exc----', exc)
    # 检查是否已包含自定义格式
    if isinstance(exc.detail, dict) and 'platform' in exc.detail and 'ret' in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # 获取路径信息
    path = request.url.path
    # platform = "unknown"
    
    # # 根据路径判断平台
    # if "wx/public" in path:
    #     platform = "WX_PUBLIC"
    # 构建标准响应格式
    response_content = _build_error_content(
        request=request,
        message=str(exc.detail),
        data={"request_method": request.method}
    )
    # 通过：获取最后一个
    error_msg = str(exc.detail).split(':')[-1].strip()
    print('error_msg----', error_msg)
    # 如果error_msg包含invalid session 说明需要调用n8n登录工作流
    if 'invalid session' in error_msg:
        # 检查锁是否已存在
        global n8n_workflow_lock
        # 获取当前时间
        current_time = datetime.now()
        print('n8n_workflow_lock----', n8n_workflow_lock)
        # 如果锁存在，但超过最大持续时间，则释放锁
        if (n8n_workflow_lock["is_running"] and n8n_workflow_lock["started_at"] 
            and (current_time - n8n_workflow_lock["started_at"]) > timedelta(seconds=n8n_workflow_lock["max_duration"])):
            print('n8n_workflow_lock----', '锁存在，但超过最大持续时间，则释放锁')
            # 释放锁
            n8n_workflow_lock["is_running"] = False
            n8n_workflow_lock["started_at"] = None
        # 如果工作流未运行，则设置锁并执行
        if not n8n_workflow_lock["is_running"]:
            try:
                # 设置锁
                n8n_workflow_lock["is_running"] = True
                n8n_workflow_lock["started_at"] = current_time
                # 调用n8n登录工作流
                # 获取n8n的webhook地址
                n8n_webhook_url = settings.N8N_WEBHOOK_URL
                async with httpx.AsyncClient() as client:
                    response = await client.get(n8n_webhook_url)
                    print('n8n_response----', response)
            except Exception as e:
                print(f"调用n8n工作流出错: {e}")
            finally:
                # 释放锁
                n8n_workflow_lock["is_running"] = False
                n8n_workflow_lock["started_at"] = None
                print('n8n_workflow_lock----', '释放锁')
        else:
            # 工作流正在运行，记录日志
            print('n8n工作流已在运行，跳过本次调用')
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    ) 

# 自定义请求参数异常处理器
# 同时处理query参数和body参数的异常处理
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    """
    统一处理请求参数异常，转换为指定格式
    支持query参数和body参数的异常处理
    """
    # 获取请求信息
    request_method = request.method
    request_url = request.url.path
    platform = _get_platform(request_url)
    raw_errors = exc.errors()

    # 将 Pydantic 原始错误翻译为统一中文提示，并保留结构化详情，方便前端展示和后端排查。
    error_details = [_build_validation_error_detail(error) for error in raw_errors]
    error_messages = [detail["message"] for detail in error_details]
    error_message = "；".join(error_messages) if error_messages else "请求参数格式错误"

    logger.warning(
        "请求参数校验失败: method={}, path={}, errors={}",
        request_method,
        request_url,
        error_details
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "platform": platform,
            "ret": [f"ERROR::请求参数校验失败: {error_message}"],
            "data": {
                "request_method": request_method,
                "errors": error_details,
            },
            "v": settings.VERSION,
            "api": request_url.strip("/")
        }
    )


# 自定义响应格式验证异常处理器
async def response_validation_error_handler(request: Request, exc: ResponseValidationError):
    """
    统一处理响应格式验证异常，转换为指定格式
    1. 检查原始返回是字典还是其他类型
    2. 如果是字典，对比字典中的字段是否有符合定义要求的，有则覆盖，没有则提取
    3. 如果不是字典，则把对应的值放到指定格式的data字段中
    4. 其余字段自动补齐
    5. 如果原始响应中包含headers字段，则将其设置为响应头
    """
    # print('response_validation_error_handler----exc----response----', request.headers)
    # print('response_validation_error_handler----exc----', exc)
    # 获取请求信息
    request_method = request.method
    request_url = request.url.path
    original_response = exc.body
    
    # 根据路径判断平台
    # platform = PlatformEnum.WX_PUBLIC if "wx/public" in request_url else "unknown"
    platform = _get_platform(request_url)
    
    # 初始化标准响应格式
    formatted_response = {
        "platform": platform,
        "api": request_url.strip("/"),
        "ret": ["SUCCESS::请求成功"],
        "v": settings.VERSION
    }
    
    # 初始化headers变量，用于存储需要设置的响应头
    response_headers = {}
    
    # 检查原始响应是否为字典类型
    if isinstance(original_response, dict):
        # 检查是否包含headers字段
        if "headers" in original_response:
            # 提取headers字段
            response_headers = original_response["headers"]
            # 从原始响应中移除headers字段
            original_response = {k: v for k, v in original_response.items() if k != "headers" and k != "cookie_str" and k != "token" and k != "cookies"}
        
        # 检查字典中是否包含符合ApiResponseData模型要求的字段
        required_fields = ["platform", "api", "data", "ret", "v"]
        existing_fields = {}
        
        for field in required_fields:
            if field in original_response:
                # 如果原始响应中包含该字段，则保留
                existing_fields[field] = original_response[field]
        
        # 如果原始响应中包含所有必要字段，则直接使用原始响应中的data字段
        if "data" in existing_fields:
            data_content = {k: v for k, v in original_response.items() if k not in existing_fields}
            # 判断data_content字典是否为空
            if len(data_content) < 1:
                formatted_response["data"] = existing_fields["data"]
            else:
                formatted_response["data"] = {
                    "data": existing_fields["data"],
                    **data_content
                }
        else:
            # 否则，将整个原始响应作为data字段的值
            # 移除已经存在于formatted_response中的字段，避免重复
            data_content = {k: v for k, v in original_response.items() if k not in existing_fields}
            formatted_response["data"] = data_content
        
        # 使用原始响应中的其他字段覆盖formatted_response中的对应字段
        for field, value in existing_fields.items():
            if field != "data":  # data字段已经单独处理
                formatted_response[field] = value
    else:
        # 如果原始响应不是字典类型，直接将其放入data字段
        formatted_response["data"] = original_response
    
    # 创建响应对象
    response = JSONResponse(
        status_code=200,  # 使用200状态码，因为这是一个有效的响应
        content=formatted_response
    )
    
    # 设置响应头
    if response_headers:
        for key, value in response_headers.items():
            if key == 'Set-Cookie' or key == 'set-cookie':
                cookie_list = []
                if isinstance(value, str):
                    cookie_list = value.split(';')
                elif isinstance(value, list):
                    cookie_list = value
                # 设置多个cookie
                for cookieValue in cookie_list:
                    # 去除左右两边空格
                    cookieValue = cookieValue.strip()
                    response.headers.append("Set-Cookie", cookieValue)
            else:
                response.headers[key] = value
    return response


# 业务异常处理器
async def auth_exception_handler(request: Request, exc: AuthException):
    """认证异常处理器"""
    logger.warning(f"认证异常: {exc.message} - 路径: {request.url.path}")
    return _business_error_response(request, exc, status.HTTP_401_UNAUTHORIZED)


async def card_exception_handler(request: Request, exc: CardException):
    """卡密异常处理器"""
    logger.warning(f"卡密异常: {exc.message} - 路径: {request.url.path}")
    return _business_error_response(request, exc, status.HTTP_400_BAD_REQUEST)


async def permission_exception_handler(request: Request, exc: PermissionException):
    """权限异常处理器"""
    logger.warning(f"权限异常: {exc.message} - 路径: {request.url.path}")
    return _business_error_response(request, exc, status.HTTP_403_FORBIDDEN)


async def user_exception_handler(request: Request, exc: UserException):
    """用户异常处理器"""
    logger.warning(f"用户异常: {exc.message} - 路径: {request.url.path}")
    return _business_error_response(request, exc, status.HTTP_400_BAD_REQUEST)


async def device_exception_handler(request: Request, exc: DeviceException):
    """设备异常处理器"""
    logger.warning(f"设备异常: {exc.message} - 路径: {request.url.path}")
    return _business_error_response(request, exc, status.HTTP_400_BAD_REQUEST)


async def app_exception_handler(request: Request, exc: AppException):
    """应用异常处理器"""
    logger.warning(f"应用异常: {exc.message} - 路径: {request.url.path}")
    return _business_error_response(request, exc, status.HTTP_400_BAD_REQUEST)


async def validation_exception_handler(request: Request, exc: ValidationException):
    """数据验证异常处理器"""
    logger.warning(f"数据验证异常: {exc.message} - 路径: {request.url.path}")
    return _business_error_response(request, exc, status.HTTP_422_UNPROCESSABLE_ENTITY)


async def database_exception_handler(request: Request, exc: DatabaseException):
    """数据库异常处理器"""
    logger.error(f"数据库异常: {exc.message} - 路径: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_content(
            request=request,
            message="数据库操作失败，请稍后重试",
            data={"code": exc.code}
        )
    )
