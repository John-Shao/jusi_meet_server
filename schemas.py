import time
from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from utils import current_timestamp_ms

# 事件类型枚举
class MessageType(StrEnum):
    CameraJoinRoom = "CameraJoinRoom"
    CameraLeaveRoom = "CameraLeaveRoom"

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


# ==================== 会议管理相关 Schemas ====================

# 预定会议请求
class BookMeetingRequest(BaseModel):
    room_id: str
    room_name: Optional[str] = None
    host_user_id: str
    host_user_name: str

# 预定会议响应
class BookMeetingResponse(BaseModel):
    code: int  # 200:成功, 400:会议已存在, 500:服务器错误
    room_id: str
    room_name: str
    message: Optional[str] = None

# 取消会议请求
class CancelMeetingRequest(BaseModel):
    room_id: str
    user_id: str  # 操作用户ID，必须是主持人

# 取消会议响应
class CancelMeetingResponse(BaseModel):
    code: int  # 200:成功, 403:权限不足, 404:房间不存在, 409:会议中有人, 500:服务器错误
    room_id: str
    message: Optional[str] = None

# 查询我的会议请求
class GetMyMeetingsRequest(BaseModel):
    user_id: str

# 会议简要信息
class MeetingInfo(BaseModel):
    room_id: str
    room_name: str
    host_user_id: str
    host_user_name: str
    start_time: int
    user_count: int  # 当前房间人数

# 查询我的会议响应
class GetMyMeetingsResponse(BaseModel):
    code: int  # 200:成功, 500:服务器错误
    meetings: List[MeetingInfo]
    total: int
    message: Optional[str] = None

# 检查房间是否存在请求
class CheckRoomRequest(BaseModel):
    room_id: str

# 检查房间是否存在响应
class CheckRoomResponse(BaseModel):
    code: int  # 200:成功, 500:服务器错误
    room_id: str
    exists: bool
    message: Optional[str] = None

# 检查用户是否在房间中请求
class CheckUserInRoomRequest(BaseModel):
    room_id: str
    user_id: str

# 检查用户是否在房间中响应
class CheckUserInRoomResponse(BaseModel):
    code: int  # 200:成功, 404:房间不存在, 500:服务器错误
    room_id: str
    user_id: str
    in_room: bool
    message: Optional[str] = None
