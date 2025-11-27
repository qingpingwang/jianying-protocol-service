"""导出任务到OSS接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from interface.utils import success_response, error_response, ErrorCode
import logging

logger = logging.getLogger(__name__)


class ExportTaskRequest(BaseModel):
    """导出任务请求"""
    task_id: str = Field(..., description="任务ID", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid"
            }
        }


def handler(
    request: ExportTaskRequest, 
    task_manager: TaskManager
) -> dict:
    """导出任务处理函数"""
    task_id = request.task_id
    
    try:
        with task_manager.get_task(task_id) as task:
            if not task:
                logger.warning(f"导出失败 - 任务不存在: {task_id}")
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": task_id})
            
            # 调用异步压缩上传（立即返回 URL）
            oss_url = task.jianyingProject.export_to_oss()
            
            logger.info(f"已创建导出任务: {task_id}, URL: {oss_url}")
            
            return success_response("导出任务已创建", {
                "task_id": task_id,
                "url": oss_url,
                "note": "文件正在后台压缩上传,预计 1-3 分钟后可访问"
            })
    except Exception as e:
        logger.error(f"创建导出任务失败: {task_id}, {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "创建导出任务失败", {"error": str(e)})

