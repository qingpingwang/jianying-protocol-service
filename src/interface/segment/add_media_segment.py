"""添加片段接口"""
from pydantic import BaseModel, Field
from typing import Optional
from task_manager import TaskManager
from utils.models import *
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class AddMediaSegmentRequest(BaseModel):
    """添加媒体片段请求"""
    task_id: str = Field(..., description="任务ID")
    track_id: str = Field(..., description="轨道ID")
    media_material: JianYingMediaMaterialInfo = Field(..., description="媒体素材信息")
    start_time: Optional[int] = Field(None, description="插入时间点（毫秒），None表示追加到轨道末尾")
    transform: Optional[SegmentTransformInfo] = Field(None, description="变换信息（缩放、旋转、平移）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "track_id": "track-uuid",
                "start_time": 0,
                "media_material": {
                    "url": "https://example.com/video.mp4",
                    "media_type": "video",
                    "speed": 1.0,
                    "mute": False,
                    "from_time": 0,
                    "to_time": -1,
                    "width": 1920,
                    "height": 1080,
                    "clip_info": {
                        "left_top_x": 100,
                        "left_top_y": 100,
                        "width": 500,
                        "height": 500
                    },
                    "adjust_info": {
                        "temperature": 0,
                        "tone": 0,
                        "saturation": 0,
                        "brightness": 0,
                        "contrast": 0,
                        "highlight": 0,
                        "shadow": 0,
                        "sharpen": 0,
                        "vignetting": 0
                    },
                    "material_name": "视频.mp4",
                    "category": "我的素材",
                    "duration": 10000
                },
                "transform": {
                    "scale_x": 1.5,
                    "scale_y": 1.5,
                    "rotate": 45,
                    "translate_x": 100,
                    "translate_y": 50
                }
            }
        }


def handler(
    request: AddMediaSegmentRequest, 
    task_manager: TaskManager
) -> dict:
    """添加片段处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            segment_id = task.jianyingProject.protocol.add_media_segment_to_track(
                track_id=request.track_id,
                media_material=request.media_material,
                start_time=request.start_time,
                transform_info=request.transform
            )
            
            logger.info(f"添加片段成功: task={request.task_id}, track={request.track_id}, segment={segment_id}")
            
            return success_response("片段添加成功", {"segment_id": segment_id})
    except Exception as e:
        logger.error(f"添加片段失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "添加片段失败", {"error": str(e)})

