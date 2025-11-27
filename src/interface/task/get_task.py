"""获取任务信息接口"""
from task_manager import TaskManager
from interface.utils import success_response, error_response, ErrorCode
import logging

logger = logging.getLogger(__name__)


def handler(
    task_id: str, 
    task_manager: TaskManager
) -> dict:
    """获取任务信息处理函数"""
    try:
        with task_manager.get_task(task_id) as task:
            if not task:
                logger.warning(f"任务不存在: {task_id}")
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": task_id})
            
            base_info = task.jianyingProject.protocol.base_info
            logger.info(f"获取任务信息: {task_id}")
            
            return success_response("获取成功", {
                "task_id": base_info.unique_id,
                "name": base_info.name,
                "width": base_info.width,
                "height": base_info.height,
                "fps": base_info.fps,
                "duration": base_info.duration
            })
    except Exception as e:
        logger.error(f"获取任务信息失败: {task_id}, {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, "获取任务信息失败", {"error": str(e)})

