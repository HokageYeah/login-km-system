from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send
import json
from typing import Any, Dict, Union, List, Callable, Awaitable
from pydantic import ValidationError
import logging
from fastapi.exceptions import ResponseValidationError

from app.schemas.common_data import ApiResponseData, PlatformEnum
from app.core.config import settings

class ResponseValidatorMiddleware(BaseHTTPMiddleware):
    """
    响应格式验证中间件
    验证所有API响应是否符合ApiResponseData格式
    如果不符合则返回错误信息和正确的格式示例
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # 只验证API路径的响应
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # 创建一个自定义的发送函数来拦截响应
        original_response = None
        response_body = []
        send_called = False
        print('ResponseValidatorMiddleware')
        
        async def send_wrapper(message):
            nonlocal original_response, response_body, send_called
            print('send_wrapper----message----', message)
            
            if message["type"] == "http.response.start":
                # 保存原始响应的状态码和头信息
                original_response = {
                    "status": message["status"],
                    "headers": message.get("headers", [])
                }
            elif message["type"] == "http.response.body":
                # 收集响应体
                response_body.append(message.get("body", b""))
                
                # 如果这是最后一个块，处理完整的响应
                if not message.get("more_body", False) and not send_called:
                    send_called = True
                    
                    # 检查是否是JSON响应
                    is_json = False
                    for header in original_response["headers"]:
                        if header[0] == b"content-type" and b"application/json" in header[1]:
                            is_json = True
                            break
                    
                    if not is_json:
                        # 如果不是JSON响应，直接返回原始响应
                        await request.send({
                            "type": "http.response.start",
                            "status": original_response["status"],
                            "headers": original_response["headers"]
                        })
                        for chunk in response_body:
                            await request.send({
                                "type": "http.response.body",
                                "body": chunk,
                                "more_body": False
                            })
                        return
                    
                    # 合并响应体并解析JSON
                    full_body = b"".join(response_body)
                    try:
                        response_data = json.loads(full_body)
                    except json.JSONDecodeError:
                        # 如果不是有效的JSON，直接返回原始响应
                        await request.send({
                            "type": "http.response.start",
                            "status": original_response["status"],
                            "headers": original_response["headers"]
                        })
                        await request.send({
                            "type": "http.response.body",
                            "body": full_body,
                            "more_body": False
                        })
                        return
                    
                    # 验证响应格式
                    try:
                        # 尝试使用ApiResponseData模型验证响应数据
                        ApiResponseData(**response_data)
                        # 如果验证通过，返回原始响应
                        await request.send({
                            "type": "http.response.start",
                            "status": original_response["status"],
                            "headers": original_response["headers"]
                        })
                        await request.send({
                            "type": "http.response.body",
                            "body": full_body,
                            "more_body": False
                        })
                    except ValidationError:
                        # 获取路径信息
                        path = request.url.path
                        platform = PlatformEnum.WX_PUBLIC if "wx/public" in path else "unknown"
                        
                        # 将原始响应数据包装到ApiResponseData格式中
                        formatted_response = {
                            "platform": platform,
                            "api": path.strip("/"),
                            "data": response_data,  # 将原始响应放入data字段
                            "ret": ["SUCCESS"],
                            "v": settings.VERSION
                        }
                        print('formatted_response-----', formatted_response)
                        # 返回格式化后的响应
                        formatted_body = json.dumps(formatted_response).encode("utf-8")

                        # 保留原始响应头中的自定义头信息
                        headers = [
                            (b"content-type", b"application/json"),
                            (b"content-length", str(len(formatted_body)).encode())
                        ]

                        # 添加原始响应头中的自定义头信息（排除content-type和content-length）
                        for header in original_response["headers"]:
                            if header[0] != b"content-type" and header[0] != b"content-length":
                                headers.append(header)
                                
                        await request.send({
                            "type": "http.response.start",
                            "status": original_response["status"],  # 保持原始状态码
                            "headers": [
                                (b"content-type", b"application/json"),
                                (b"content-length", str(len(formatted_body)).encode())
                            ]
                        })
                        await request.send({
                            "type": "http.response.body",
                            "body": formatted_body,
                            "more_body": False
                        })
            
            # 将消息传递给原始的发送函数
            if not send_called:
                await request.send(message)
        print('send_wrapper')
        # 使用自定义的发送函数调用下一个中间件
        request.send = send_wrapper
        return await call_next(request)