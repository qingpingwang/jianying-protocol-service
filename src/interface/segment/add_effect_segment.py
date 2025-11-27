"""添加视频特效片段接口"""
from pydantic import BaseModel, Field
from typing import Optional
from task_manager import TaskManager
from utils.models import *
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class AddEffectSegmentRequest(BaseModel):
    """添加视频特效片段请求"""
    task_id: str = Field(..., description="任务ID")
    track_id: str = Field(..., description="特效轨道ID")
    effect_material: JianYingInternalMaterialInfo = Field(..., description="视频特效材质信息")
    start_time: Optional[int] = Field(None, description="插入时间点（毫秒），None表示追加到轨道末尾")
    duration: int = Field(5000, description="特效时长（毫秒）", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "track_id": "effect-track-uuid",
                "start_time": 0,
                "duration": 10000,
                "effect_material": {
                    "material_info": {
                        "type": "video_effect",
                        "effect_id": "1520514",
                        "name": "放大镜",
                        "category_id": "39654",
                        "category_name": "热门",
                        "apply_target_type": 2,
                        "value": 1.0,
                        "adjust_params": [
                            {
                                "name": "effects_adjust_size",
                                "value": 0.5,
                                "default_value": 0.5
                            }
                        ],
                        "path": "...",
                        "platform": "all",
                        "resource_id": "7051836120224502308"
                    }
                }
            }
        }


def handler(
    request: AddEffectSegmentRequest, 
    task_manager: TaskManager
) -> dict:
    """添加视频特效片段处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            segment_id = task.jianyingProject.protocol.add_effect_segment_to_track(
                track_id=request.track_id,
                effect_material=request.effect_material,
                start_time=request.start_time,
                duration=request.duration
            )
            
            logger.info(f"添加视频特效片段成功: task={request.task_id}, track={request.track_id}, segment={segment_id}")
            
            return success_response("视频特效片段添加成功", {"segment_id": segment_id})
    except Exception as e:
        logger.error(f"添加视频特效片段失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "添加视频特效片段失败", {"error": str(e)})

