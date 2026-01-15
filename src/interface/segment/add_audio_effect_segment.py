"""添加音效片段接口"""
from pydantic import BaseModel, Field
from typing import Optional
from task_manager import TaskManager
from utils.models import *
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class AddAudioEffectSegmentRequest(BaseModel):
    """添加音效片段请求"""
    task_id: str = Field(..., description="任务ID")
    track_id: str = Field(..., description="音频轨道ID")
    audio_material: dict = Field(..., description="音效素材信息")
    start_time: Optional[int] = Field(None, description="插入时间点（毫秒），None表示追加到轨道末尾")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "track_id": "audio-track-uuid",
                "start_time": 0,
                "audio_material": {
                    "aigc_history_id": "",
                    "aigc_item_id": "",
                    "app_id": 1775,
                    "category_id": "heycan_search_sound",
                    "category_name": "heycan_search_sound",
                    "check_flag": 1,
                    "copyright_limit_type": "none",
                    "duration": 1566666,
                    "effect_id": "6896679322715819278",
                    "formula_id": "",
                    "id": "9EB7F987-8DEA-4C89-9CA4-B053F4F36E3C",
                    "intensifies_path": "",
                    "is_ai_clone_tone": False,
                    "is_text_edit_overdub": False,
                    "is_ugc": False,
                    "local_material_id": "",
                    "music_id": "",
                    "name": "任务完成",
                    "path": "/Users/who/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/music/93a6b50a8e0fec1cbf71e8283a3d0caa.mp3",
                    "query": "",
                    "request_id": "2025070916171852767A736BABABADE271",
                    "resource_id": "",
                    "search_id": "",
                    "source_from": "",
                    "source_platform": 1,
                    "team_id": "",
                    "text_id": "",
                    "tone_category_id": "",
                    "tone_category_name": "",
                    "tone_effect_id": "",
                    "tone_effect_name": "",
                    "tone_platform": "",
                    "tone_second_category_id": "",
                    "tone_second_category_name": "",
                    "tone_speaker": "",
                    "tone_type": "",
                    "type": "sound",
                    "video_id": "",
                    "wave_points": [],
                    "clioo_url": "https://mogic-algo-data.getmogic.com/jy-resources/audio/%E4%BB%BB%E5%8A%A1%E5%AE%8C%E6%88%90-93a6b50a8e0fec1cbf71e8283a3d0caa.mp3"
                }
            }
        }


def handler(
    request: AddAudioEffectSegmentRequest, 
    task_manager: TaskManager
) -> dict:
    """添加音效片段处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            segment_id = task.jianyingProject.protocol.add_audio_effect_segment_to_track(
                track_id=request.track_id,
                audio_material=request.audio_material,
                start_time=request.start_time,
            )
            
            logger.info(f"添加音效片段成功: task={request.task_id}, track={request.track_id}, segment={segment_id}")
            
            return success_response("音效片段添加成功", {"segment_id": segment_id})
    except Exception as e:
        logger.error(f"添加音效片段失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "添加音效片段失败", {"error": str(e)})


