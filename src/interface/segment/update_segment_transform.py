"""更新片段变换信息接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from utils.models import SegmentTransformInfo
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class UpdateSegmentTransformRequest(BaseModel):
    """更新片段变换信息请求"""
    task_id: str = Field(..., description="任务ID")
    segment_id: str = Field(..., description="片段ID")
    transform: SegmentTransformInfo = Field(..., description="变换信息（缩放、旋转、平移）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "segment_id": "segment-uuid",
                "transform": {
                    "translate_x": 0.0,
                    "translate_y": 0.0,
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                    "rotate": 0.0
                }
            }
        }


def handler(
    request: UpdateSegmentTransformRequest,
    task_manager: TaskManager
) -> dict:
    """更新片段变换信息处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task not found: {request.task_id}"
                )
            
            # 更新变换信息
            segment_id = task.jianyingProject.protocol.update_segment_transform_info(
                segment_id=request.segment_id,
                transform_info=request.transform
            )
            
            return success_response({
                "segment_id": segment_id,
                "message": "Segment transform updated successfully"
            })
            
    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return error_response(ErrorCode.VALIDATION_ERROR, str(e))
    except Exception as e:
        logger.error(f"Update segment transform failed: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))

