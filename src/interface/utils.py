"""
接口公共工具

提供所有接口共用的响应模型、辅助函数
"""
from pydantic import BaseModel, Field
from typing import Optional


# ==================== 统一响应模型 ====================
class BaseResponse(BaseModel):
    """
    统一响应基类
    
    所有 API 接口都返回此格式
    """
    code: int = Field(..., description="业务状态码：0=成功，其他=失败")
    message: str = Field(..., description="响应消息，人类可读的提示信息")
    data: Optional[dict] = Field(None, description="响应数据，具体内容根据接口而定")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "成功示例",
                    "value": {
                        "code": 0,
                        "message": "操作成功",
                        "data": {"task_id": "task-uuid"}
                    }
                },
                {
                    "summary": "失败示例",
                    "value": {
                        "code": 404,
                        "message": "任务不存在",
                        "data": {"task_id": "invalid-id"}
                    }
                }
            ]
        }


# ==================== 响应构建函数 ====================
def success_response(message: str = "成功", data: dict = None) -> dict:
    """
    构建成功响应
    
    Args:
        message: 成功消息
        data: 响应数据
        
    Returns:
        标准格式的成功响应字典
        
    Example:
        >>> success_response("创建成功", {"task_id": "xxx"})
        {"code": 0, "message": "创建成功", "data": {"task_id": "xxx"}}
    """
    return {
        "code": 0,
        "message": message,
        "data": data or {}
    }


def error_response(code: int, message: str, data: dict = None) -> dict:
    """
    构建错误响应
    
    Args:
        code: 错误码（非0）
        message: 错误消息
        data: 错误详情
        
    Returns:
        标准格式的错误响应字典
        
    Example:
        >>> error_response(404, "任务不存在", {"task_id": "xxx"})
        {"code": 404, "message": "任务不存在", "data": {"task_id": "xxx"}}
    """
    return {
        "code": code,
        "message": message,
        "data": data or {}
    }


# ==================== 常用错误码 ====================
class ErrorCode:
    """错误码常量"""
    SUCCESS = 0
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403

