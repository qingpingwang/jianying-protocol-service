"""根据索引获取轨道接口"""
from task_manager import TaskManager
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


def handler(task_id: str, index: int, task_manager: TaskManager):
    """根据索引获取轨道处理函数"""
    try:
        with task_manager.get_task(task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": task_id})
            
            track = task.jianyingProject.protocol.get_track_by_index(index)
            
            if not track:
                return error_response(ErrorCode.NOT_FOUND, "轨道不存在", {"index": index})
            
            logger.info(f"根据索引获取轨道: task={task_id}, index={index}")
            
            return success_response("获取成功", {"track": track})
    except Exception as e:
        logger.error(f"根据索引获取轨道失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "根据索引获取轨道失败", {"error": str(e)})

