"""获取轨道详情接口"""
from task_manager import TaskManager
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


def handler(task_id: str, track_id: str, task_manager: TaskManager):
    """获取轨道详情处理函数"""
    try:
        with task_manager.get_task(task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": task_id})
            
            track = task.jianyingProject.protocol.get_track_by_id(track_id)
            
            if not track:
                return error_response(ErrorCode.NOT_FOUND, "轨道不存在", {"track_id": track_id})
            
            logger.info(f"获取轨道详情: task={task_id}, track={track_id}")
            
            return success_response("获取成功", {"track": track})
    except Exception as e:
        logger.error(f"获取轨道详情失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "获取轨道详情失败", {"error": str(e)})

