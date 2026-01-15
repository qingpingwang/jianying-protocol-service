"""更新文本素材信息接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from utils.models import JianYingTextMaterialInfo
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class UpdateTextContentRequest(BaseModel):
    """更新文本素材信息请求"""
    task_id: str = Field(..., description="任务ID")
    segment_id: str = Field(..., description="文本片段ID")
    text: str = Field(..., description="新的文本内容")
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid", 
                "segment_id": "segment-uuid",
                "text": "新的文本内容"
            }
        }


def handler(
    request: UpdateTextContentRequest,
    task_manager: TaskManager
) -> dict:
    """更新文本内容处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task not found: {request.task_id}"
                )
            
            # 更新文本素材信息
            segment_id = task.jianyingProject.protocol.update_text_content(
                segment_id=request.segment_id,
                text=request.text
            )
            
            return success_response({
                "segment_id": segment_id,
                "message": "Text content updated successfully"
            })
            
    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return error_response(ErrorCode.VALIDATION_ERROR, str(e))
    except Exception as e:
        logger.error(f"Update text content failed: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))

