from pydantic import BaseModel
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

T = TypeVar('T')  # 定义泛型


class ResponseModel(Generic[T], BaseModel):
    """统一响应模型"""
    status_code: int
    status_message: str
    data: T = None


def resp_200(code: int = 200,
             message: str = 'SUCCESS',
             data: Union[list, dict, str, Any] = None) -> ResponseModel:
    """返回成功响应"""
    return ResponseModel(status_code=code, status_message=message, data=data)


def resp_500(code: int = 500,
             message: str = 'BAD REQUEST',
             data: Union[list, dict, str, Any] = None) -> ResponseModel:
    """返回失败响应"""
    return ResponseModel(status_code=code, status_message=message, data=data)