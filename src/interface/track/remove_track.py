"""删除轨道接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class RemoveTrackRequest(BaseModel):
    """删除轨道请求"""
    task_id: str = Field(..., description="任务ID")
    track_id: str = Field(..., description="轨道ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "track_id": "track-uuid"
            }
        }


def handler(request: RemoveTrackRequest, task_manager: TaskManager):
    """删除轨道处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            success = task.jianyingProject.protocol.remove_track(request.track_id)
            
            if not success:
                return error_response(ErrorCode.NOT_FOUND, "轨道不存在", {"track_id": request.track_id})
            
            logger.info(f"删除轨道成功: task={request.task_id}, track={request.track_id}")
            
            return success_response("轨道删除成功", {"track_id": request.track_id})
    except Exception as e:
        logger.error(f"删除轨道失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "删除轨道失败", {"error": str(e)})

