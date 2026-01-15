"""删除任务接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from interface.utils import success_response, error_response, ErrorCode
import logging

logger = logging.getLogger(__name__)


class RemoveTaskRequest(BaseModel):
    """删除任务请求"""
    task_id: str = Field(..., description="任务ID", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid"
            }
        }


def handler(
    request: RemoveTaskRequest, 
    task_manager: TaskManager
) -> dict:
    """删除任务处理函数"""
    task_id = request.task_id
    
    try:
        # 删除任务
        if not task_manager.remove_task(task_id):
            logger.error(f"删除任务失败: {task_id}")
            return error_response(ErrorCode.INTERNAL_ERROR, "删除任务失败", {"task_id": task_id})
        
        logger.info(f"任务删除成功: {task_id}")
        
        return success_response("任务删除成功", {
            "task_id": task_id,
            "deleted": True
        })
    except Exception as e:
        logger.error(f"删除任务失败: {task_id}, {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "删除任务失败", {"error": str(e)})

