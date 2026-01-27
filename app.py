'''
面向APP提供的API接口
'''
import logging
from fastapi import APIRouter, Response
from vertc_client import rtc_client
from config import settings
from schemas import *


logger = logging.getLogger(__name__)

app_router = APIRouter()

# 处理APP请求
@app_router.post("/app", response_model=ResponseMessageBase)
async def handle_app_request(request: RequestMessageBase):

    # 根据不同的事件名称处理不同的消息
    handler = REQUEST_HANDLERS.get(request.type)
    if handler:
        return await handler(request, request.data)
    else:
        logger.warning(f"收到未知事件消息: {request.type}")
        return ResponseMessageBase(type=request.type, code=400, message="未知事件类型")


# 处理用户加入房间事件
async def handle_camera_join_room(request: RequestMessageBase, req_data: Dict[str, Any]):
    data = CameraJoinRequest(**req_data)
    rtmp_url = f"rtmp://{settings.audio_rtmp_host}:{settings.audio_rtmp_port}/live/{data.device_sn}"
    relay_url = f"rtmp://{settings.video_rtmp_host}:{settings.video_rtmp_port}/live/{data.device_sn}"
    rtsp_url = f"rtsp://{settings.video_rtmp_host}:{settings.video_rtmp_port}/live_{data.device_sn}"

    # 启动合流转推
    response = rtc_client.start_push_mixed_stream(
        room_id=data.room_id,
        user_id=data.user_id,  # 排除的用户ID
        task_id=data.device_sn,
        push_url=rtmp_url,
    )

    logger.info(f"启动合流转推: {response}")
    
    # 启动在线媒体流输入
    response = rtc_client.start_relay_stream(
        room_id=data.room_id,
        user_id=data.user_id,  # 在线媒体流输入的用户ID
        task_id=data.device_sn,
        stream_url=relay_url,
    )

    logger.info(f"启动在线媒体流输入: {response}")

    # 启动实时对话式AI
    '''
    response = rtc_client.start_voice_chat(
        room_id=data.room_id,
        bot_id=data.device_sn,
        user_id=data.user_id,
        task_id=data.device_sn,
        dialog_id=data.device_sn,
    )
    '''

    data = CameraJoinResponse(
        rtmp_url=rtmp_url,
        rtsp_url=rtsp_url,
    )

    return ResponseMessageBase(type=request.type, data=data)


async def handle_camera_leave_room(request: RequestMessageBase, req_data: Dict[str, Any]):
    data = CameraLeaveRequest(**req_data)
    # 停止合流转推
    response = rtc_client.stop_push_stream_to_cdn(
        room_id=data.room_id,
        task_id=data.device_sn
    )

    logger.info(f"停止合流转推: {response}")

    # 停止在线媒体流输入
    response = rtc_client.stop_relay_stream(
        room_id=data.room_id,
        task_id=data.device_sn
    )

    logger.info(f"停止在线媒体流输入: {response}")

    # 关闭实时对话式AI
    '''
    response = rtc_client.stop_voice_chat(
        room_id=data.room_id,
        task_id=data.device_sn
    )

    logger.info(f"关闭实时对话式AI: {response}")
    '''
    return ResponseMessageBase(type=request.type)


# 处理程序映射
REQUEST_HANDLERS = {
    MessageType.CameraJoinRoom: handle_camera_join_room,
    MessageType.CameraLeaveRoom: handle_camera_leave_room,
}
