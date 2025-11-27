"""获取轨道数量接口"""
from task_manager import TaskManager
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


def handler(task_id: str, task_manager: TaskManager):
    """获取轨道数量处理函数"""
    try:
        with task_manager.get_task(task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": task_id})
            
            count = task.jianyingProject.protocol.track_size
            
            logger.info(f"获取轨道数量: task={task_id}, count={count}")
            
            return success_response("获取成功", {"count": count})
    except Exception as e:
        logger.error(f"获取轨道数量失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "获取轨道数量失败", {"error": str(e)})

