"""添加滤镜片段接口"""
from pydantic import BaseModel, Field
from typing import Optional
from task_manager import TaskManager
from utils.models import *
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class AddFilterSegmentRequest(BaseModel):
    """添加滤镜片段请求"""
    task_id: str = Field(..., description="任务ID")
    track_id: str = Field(..., description="滤镜轨道ID")
    filter_material: JianYingInternalMaterialInfo = Field(..., description="滤镜材质信息")
    start_time: Optional[int] = Field(None, description="插入时间点（毫秒），None表示追加到轨道末尾")
    duration: int = Field(5000, description="滤镜时长（毫秒）", gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "track_id": "filter-track-uuid",
                "start_time": 0,
                "duration": 10000,
                "filter_material": {
                    "material_info": {
                        "type": "filter",
                        "effect_id": "7426668776491453707",
                        "name": "高清增强",
                        "category_id": "10494",
                        "category_name": "人像",
                        "value": 1.0,
                        "path": "...",
                        "platform": "all",
                        "resource_id": "7426668776491453707"
                    }
                }
            }
        }


def handler(
    request: AddFilterSegmentRequest, 
    task_manager: TaskManager
) -> dict:
    """添加滤镜片段处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            segment_id = task.jianyingProject.protocol.add_filter_segment_to_track(
                track_id=request.track_id,
                filter_material=request.filter_material,
                start_time=request.start_time,
                duration=request.duration
            )
            
            logger.info(f"添加滤镜片段成功: task={request.task_id}, track={request.track_id}, segment={segment_id}")
            
            return success_response("滤镜片段添加成功", {"segment_id": segment_id})
    except Exception as e:
        logger.error(f"添加滤镜片段失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "添加滤镜片段失败", {"error": str(e)})

