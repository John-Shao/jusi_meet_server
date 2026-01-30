from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # 接收X5设备推送视频流的RTMP服务器地址和端口
    video_rtmp_host: str
    video_rtmp_port: int
    
    # 接收VeRTC推送音频流的RTMP服务器地址和端口
    audio_rtmp_host: str
    audio_rtmp_port: int
    audio_rtsp_port: int
    # VolcEngine RTC 配置
    volc_rtc_app_id: str
    volc_rtc_app_key: str
    volc_token_expire_seconds: int = 3600  # 默认1小时

    # 音视频互动智能体（Conversational-AI）
    volc_cai_app_id: str
    volc_cai_app_key: str

    # 豆包端到端实时语音大模型
    doubao_s2s_app_id: str
    doubao_s2s_access_token: str

    # AK/SK
    volc_ak: str
    volc_sk: str
    volc_region: str
    
    # 服务器配置
    app_name: str = "JUSI Meet Server"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    bind_addr: str = "0.0.0.0"
    bind_port: int = 9006
    debug: bool = True

    # RTS 服务配置
    rts_service_url: str = "http://localhost:9000"  # jusi_meet_rts 服务地址
    
    # 指定配置文件和相关参数
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False

# 创建配置实例
settings = Settings()
