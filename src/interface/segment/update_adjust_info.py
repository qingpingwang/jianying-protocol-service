"""更新片段调色信息接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from utils.models import AdjustInfo
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class UpdateAdjustInfoRequest(BaseModel):
    """更新片段调色信息请求"""
    task_id: str = Field(..., description="任务ID")
    segment_id: str = Field(..., description="视频片段ID")
    adjust_info: AdjustInfo = Field(..., description="调色信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "segment_id": "segment-uuid",
                "adjust_info": {
                    "brightness": 0,
                    "contrast": 0,
                    "saturation": 0,
                    "sharpen": 0,
                    "highlights": 0,
                    "shadows": 0,
                    "temperature": 0,
                    "tint": 0,
                    "fade": 0,
                    "hue": 0,
                    "vignette": 0
                }
            }
        }


def handler(
    request: UpdateAdjustInfoRequest,
    task_manager: TaskManager
) -> dict:
    """更新片段调色信息处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task not found: {request.task_id}"
                )
            
            # 更新调色信息
            segment_id = task.jianyingProject.protocol.update_segment_adjust_info(
                segment_id=request.segment_id,
                adjust_info=request.adjust_info
            )
            
            return success_response({
                "segment_id": segment_id,
                "message": "Adjust info updated successfully"
            })
            
    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return error_response(ErrorCode.VALIDATION_ERROR, str(e))
    except Exception as e:
        logger.error(f"Update adjust info failed: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))

