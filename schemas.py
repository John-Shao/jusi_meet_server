import time
from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from utils import current_timestamp_ms

# 事件类型枚举
class MessageType(StrEnum):
    CameraJoinRoom = "CameraJoinRoom"
    CameraLeaveRoom = "CameraLeaveRoom"

# 请求消息模型
class RequestMessageBase(BaseModel):
    type: str
    timestamp: int = Field(default_factory=lambda: current_timestamp_ms())  # 时间戳ms
    data: Optional[Any] = {}

# 响应消息模型
class ResponseMessageBase(BaseModel):
    type: str
    code: int = 200
    message: str = "ok"  # 详细错误信息
    timestamp: int = Field(default_factory=lambda: current_timestamp_ms())  # 时间戳ms
    data: Optional[Any] = {}


# 相机加入房间请求
class CameraJoinRequest(BaseModel):
    user_id: str = Field(description="用户ID")
    room_id: str = Field(description="房间ID")
    device_sn: str = Field(description="设备序列号")

# 相机加入房间响应
class CameraJoinResponse(BaseModel):
    rtmp_url: str = Field(description="RTMP URL")
    rtsp_url: str = Field(description="RTSP URL")


# 相机离开房间请求
class CameraLeaveRequest(BaseModel):
    user_id: str = Field(description="用户ID")
    room_id: str = Field(description="房间ID")
    device_sn: str = Field(description="设备序列号")

# 相机离开房间响应
class CameraLeaveResponse(BaseModel):
    pass
