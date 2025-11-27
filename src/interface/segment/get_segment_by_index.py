"""根据索引获取片段接口"""
from task_manager import TaskManager
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


def handler(
    task_id: str, 
    track_id: str, 
    index: int, 
    task_manager: TaskManager
) -> dict:
    """根据索引获取片段处理函数"""
    try:
        with task_manager.get_task(task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": task_id})
            
            segment = task.jianyingProject.protocol.get_segment_by_index(track_id, index)
            
            if not segment:
                return error_response(ErrorCode.NOT_FOUND, "片段不存在", {"track_id": track_id, "index": index})
            
            logger.info(f"根据索引获取片段: task={task_id}, track={track_id}, index={index}")
            
            return success_response("获取成功", {"segment": segment})
    except ValueError as e:
        logger.warning(f"根据索引获取片段失败: {e}")
        return error_response(ErrorCode.NOT_FOUND, str(e), {"track_id": track_id})
    except Exception as e:
        logger.error(f"根据索引获取片段失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "根据索引获取片段失败", {"error": str(e)})

