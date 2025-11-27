"""删除片段接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class RemoveSegmentRequest(BaseModel):
    """删除片段请求"""
    task_id: str = Field(..., description="任务ID")
    segment_id: str = Field(..., description="片段ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "segment_id": "segment-uuid"
            }
        }


def handler(
    request: RemoveSegmentRequest, 
    task_manager: TaskManager
) -> dict:
    """删除片段处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            success = task.jianyingProject.protocol.remove_segment_by_id(request.segment_id)
            
            if not success:
                return error_response(ErrorCode.NOT_FOUND, "片段不存在", {"segment_id": request.segment_id})
            
            logger.info(f"删除片段成功: task={request.task_id}, segment={request.segment_id}")
            
            return success_response("片段删除成功", {"segment_id": request.segment_id})
    except Exception as e:
        logger.error(f"删除片段失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "删除片段失败", {"error": str(e)})

