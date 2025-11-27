"""获取轨道列表接口"""
from task_manager import TaskManager
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


def handler(task_id: str, task_manager: TaskManager):
    """获取轨道列表处理函数"""
    try:
        with task_manager.get_task(task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": task_id})
            
            tracks = task.jianyingProject.protocol.get_track_list()
            
            logger.info(f"获取轨道列表: task={task_id}, count={len(tracks)}")
            
            return success_response("获取成功", {"tracks": tracks})
    except Exception as e:
        logger.error(f"获取轨道列表失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "获取轨道列表失败", {"error": str(e)})

