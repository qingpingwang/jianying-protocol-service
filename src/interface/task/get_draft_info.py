"""获取草稿信息接口"""
from task_manager import TaskManager
from interface.utils import success_response, error_response, ErrorCode
import logging

logger = logging.getLogger(__name__)


def handler(
    task_id: str, 
    task_manager: TaskManager
) -> dict:
    """获取草稿信息处理函数"""
    try:
        with task_manager.get_task(task_id) as task:
            if not task:
                logger.warning(f"任务不存在: {task_id}")
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": task_id})
            
            logger.info(f"获取草稿数据: {task_id}")
            return success_response("获取成功", task.jianyingProject.protocol.draft_info)
    except Exception as e:
        logger.error(f"获取草稿信息失败: {task_id}, {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, "获取草稿信息失败", {"error": str(e)})

