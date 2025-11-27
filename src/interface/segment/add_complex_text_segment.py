"""添加复杂文本片段接口"""
from pydantic import BaseModel, Field
from typing import Optional
from task_manager import TaskManager
from utils.models import *
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class AddComplexTextSegmentRequest(BaseModel):
    """添加复杂文本片段请求"""
    task_id: str = Field(..., description="任务ID")
    track_id: str = Field(..., description="轨道ID")
    complex_text_material: JianYingTextComplexStyle = Field(..., description="复杂文本样式信息")
    start_time: Optional[int] = Field(None, description="插入时间点（毫秒），None表示追加到轨道末尾")
    duration: int = Field(3000, description="文本显示时长（毫秒）", gt=0)
    transform: Optional[SegmentTransformInfo] = Field(None, description="变换信息（缩放、旋转、平移）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "track_id": "track-uuid",
                "start_time": 0,
                "duration": 3000,
                "complex_text_material": {
                    "text": "默认文本",
                    "complex_style_info": {
                        "text_segment": {},
                        "materials": {}
                    }
                },
                "transform": {
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                    "rotate": 0,
                    "translate_x": 0.0,
                    "translate_y": -0.3
                }
            }
        }


def handler(
    request: AddComplexTextSegmentRequest, 
    task_manager: TaskManager
) -> dict:
    """添加复杂文本片段处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            segment_id = task.jianyingProject.protocol.add_complex_text_segment_to_track(
                track_id=request.track_id,
                complex_text_material=request.complex_text_material,
                start_time=request.start_time,
                duration=request.duration,
                transform_info=request.transform
            )
            
            logger.info(f"添加复杂文本片段成功: task={request.task_id}, track={request.track_id}, segment={segment_id}")
            
            return success_response("复杂文本片段添加成功", {"segment_id": segment_id})
    except Exception as e:
        logger.error(f"添加复杂文本片段失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "添加复杂文本片段失败", {"error": str(e)})

