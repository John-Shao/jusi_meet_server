'''
面向APP提供的API接口
'''
import logging
from fastapi import APIRouter, Response
from vertc_client import rtc_client
from config import settings
from schemas import *


logger = logging.getLogger(__name__)

drift_router = APIRouter()


# 摄像头加入房间接口
@drift_router.post("/camera/join", response_model=ResponseMessageBase)
async def camera_join_room(data: CameraJoinRequest):
    # 上行媒体流
    up_rtmp_url = f"rtmp://{settings.video_rtmp_host}:{settings.video_rtmp_port}/live/{data.device_sn}"
    # 下行媒体流
    dn_rtmp_url = f"rtmp://{settings.audio_rtmp_host}:{settings.audio_rtmp_port}/live/{data.device_sn}"
    dn_rtsp_url = f"rtsp://{settings.audio_rtmp_host}:{settings.audio_rtsp_port}/live_{data.device_sn}"

    try:
        # 启动合流转推
        response = rtc_client.start_push_mixed_stream(
            room_id=data.room_id,
            user_id=data.user_id,  # 排除的用户ID
            task_id=data.device_sn,
            push_url=dn_rtmp_url,
        )

        logger.info(f"启动合流转推: {response}")

        # 启动在线媒体流输入
        response = rtc_client.start_relay_stream(
            room_id=data.room_id,
            user_id=data.user_id,  # 在线媒体流输入的用户ID
            task_id=data.device_sn,
            stream_url=up_rtmp_url,
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

        response_data = CameraJoinResponse(
            rtmp_url=up_rtmp_url,
            rtsp_url=dn_rtsp_url,
        )

        return ResponseMessageBase(type=MessageType.CameraJoinRoom, data=response_data)

    except Exception as e:
        logger.error(f"处理CameraJoinRoom请求失败: {str(e)}")
        return ResponseMessageBase(
            type=MessageType.CameraJoinRoom,
            code=500,
            message=f"启动RTC服务失败: {str(e)}"
        )


# 摄像头离开房间接口
@drift_router.post("/camera/leave", response_model=ResponseMessageBase)
async def camera_leave_room(data: CameraLeaveRequest):

    try:
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
        return ResponseMessageBase(type=MessageType.CameraLeaveRoom)

    except Exception as e:
        logger.error(f"处理CameraLeaveRoom请求失败: {str(e)}")
        return ResponseMessageBase(
            type=MessageType.CameraLeaveRoom,
            code=500,
            message=f"停止RTC服务失败: {str(e)}"
        )
