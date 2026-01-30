"""
会议管理API
提供会议预定、取消、查询等功能
通过 HTTP 调用 jusi_meet_rts 服务
"""
import logging
import httpx
from fastapi import APIRouter
from schemas import *
from config import settings

logger = logging.getLogger(__name__)

meeting_router = APIRouter()


# 创建 HTTP 客户端
async def call_rts_service(method: str, endpoint: str, data: dict = None) -> dict:
    """
    调用 RTS 服务的通用方法

    Args:
        method: HTTP 方法 (GET/POST)
        endpoint: API 端点
        data: 请求数据

    Returns:
        响应数据
    """
    url = f"{settings.rts_service_url}{settings.api_prefix}{endpoint}"

    logger.info(f"调用RTS服务: {method} {url} 数据: {data}")

    # 设置请求头
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # 禁用代理，避免 localhost 请求被系统代理拦截
        async with httpx.AsyncClient(timeout=10.0, trust_env=False) as client:
            if method == "POST":
                response = await client.post(url, json=data, headers=headers)
            else:
                response = await client.get(url, params=data, headers=headers)

            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"RTS服务返回错误 {e.response.status_code}: {e.response.text}")
        return {"code": e.response.status_code, "message": f"RTS服务错误: {e.response.text}"}
    except Exception as e:
        logger.error(f"调用RTS服务失败: {str(e)}")
        return {"code": 500, "message": f"调用RTS服务失败: {str(e)}"}


# 预定会议
@meeting_router.post("meeting/book", response_model=BookMeetingResponse)
async def book_meeting(request: BookMeetingRequest):
    """
    预定会议

    Args:
        request: 预定会议请求

    Returns:
        预定结果
    """
    try:
        result = await call_rts_service(
            "POST",
            "/meeting/book",
            request.model_dump()
        )

        # 检查 RTS 服务是否返回错误
        if result.get("code") != 200 and "room_id" not in result:
            error_msg = result.get("message", "RTS服务返回错误")
            logger.error(f"RTS服务返回错误: {error_msg}")
            return BookMeetingResponse(
                code=500,
                room_id=request.room_id,
                room_name=request.room_name or request.room_id,
                message=error_msg
            )

        return BookMeetingResponse(**result)
    except Exception as e:
        logger.error(f"预定会议失败: {e}")
        return BookMeetingResponse(
            code=500,
            room_id=request.room_id,
            room_name=request.room_name or request.room_id,
            message=f"服务器错误: {str(e)}"
        )


# 取消会议
@meeting_router.post("meeting/cancel", response_model=CancelMeetingResponse)
async def cancel_meeting(request: CancelMeetingRequest):
    """
    取消会议（只有主持人可以取消，且房间内没有人时才能取消）

    Args:
        request: 取消会议请求

    Returns:
        取消结果
    """
    try:
        result = await call_rts_service(
            "POST",
            "/meeting/cancel",
            request.model_dump()
        )

        # 检查 RTS 服务是否返回错误
        if result.get("code") != 200 and "room_id" not in result:
            error_msg = result.get("message", "RTS服务返回错误")
            logger.error(f"RTS服务返回错误: {error_msg}")
            return CancelMeetingResponse(
                code=500,
                room_id=request.room_id,
                message=error_msg
            )

        return CancelMeetingResponse(**result)
    except Exception as e:
        logger.error(f"取消会议失败: {e}")
        return CancelMeetingResponse(
            code=500,
            room_id=request.room_id,
            message=f"服务器错误: {str(e)}"
        )


# 查询我的会议
@meeting_router.post("meeting/get-my", response_model=GetMyMeetingsResponse)
async def get_my_meetings(request: GetMyMeetingsRequest):
    """
    查询用户作为主持人的所有会议

    Args:
        request: 查询会议请求

    Returns:
        会议列表
    """
    try:
        result = await call_rts_service(
            "POST",
            "/meeting/get-my",
            request.model_dump()
        )

        # 检查 RTS 服务是否返回错误
        if result.get("code") != 200 and "meetings" not in result:
            error_msg = result.get("message", "RTS服务返回错误")
            logger.error(f"RTS服务返回错误: {error_msg}")
            return GetMyMeetingsResponse(
                code=500,
                meetings=[],
                total=0,
                message=error_msg
            )

        return GetMyMeetingsResponse(**result)
    except Exception as e:
        logger.error(f"查询会议失败: {e}")
        return GetMyMeetingsResponse(
            code=500,
            meetings=[],
            total=0,
            message=f"服务器错误: {str(e)}"
        )


# 检查房间是否存在
@meeting_router.post("/meeting/check-room", response_model=CheckRoomResponse)
async def check_room(request: CheckRoomRequest):
    """
    检查房间号是否存在

    Args:
        request: 检查房间请求

    Returns:
        房间是否存在
    """
    try:
        result = await call_rts_service(
            "POST",
            "/meeting/check-room",
            request.model_dump()
        )

        # 检查 RTS 服务是否返回错误
        if result.get("code") != 200 and "room_id" not in result:
            error_msg = result.get("message", "RTS服务返回错误")
            logger.error(f"RTS服务返回错误: {error_msg}")
            return CheckRoomResponse(
                code=500,
                room_id=request.room_id,
                exists=False,
                message=error_msg
            )

        return CheckRoomResponse(**result)
    except Exception as e:
        logger.error(f"检查房间失败: {e}")
        return CheckRoomResponse(
            code=500,
            room_id=request.room_id,
            exists=False,
            message=f"服务器错误: {str(e)}"
        )


# 检查用户是否在房间中
@meeting_router.post("/meeting/check-user-in-room", response_model=CheckUserInRoomResponse)
async def check_user_in_room(request: CheckUserInRoomRequest):
    """
    检查用户是否在某个会议中

    Args:
        request: 检查用户在房间请求

    Returns:
        用户是否在房间中
    """
    try:
        result = await call_rts_service(
            "POST",
            "/meeting/check-user-in-room",
            request.model_dump()
        )

        # 检查 RTS 服务是否返回错误
        if result.get("code") != 200 and "in_room" not in result:
            error_msg = result.get("message", "RTS服务返回错误")
            logger.error(f"RTS服务返回错误: {error_msg}")
            return CheckUserInRoomResponse(
                code=500,
                room_id=request.room_id,
                user_id=request.user_id,
                in_room=False,
                message=error_msg
            )

        return CheckUserInRoomResponse(**result)
    except Exception as e:
        logger.error(f"检查用户是否在房间失败: {e}")
        return CheckUserInRoomResponse(
            code=500,
            room_id=request.room_id,
            user_id=request.user_id,
            in_room=False,
            message=f"服务器错误: {str(e)}"
        )
