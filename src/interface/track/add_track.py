"""创建轨道接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class AddTrackRequest(BaseModel):
    """创建轨道请求"""
    task_id: str = Field(..., description="任务ID")
    track_type: str = Field(..., description="轨道类型：audio/video/effect/text/sticker/adjust")
    index: int = Field(-1, description="插入位置，-1表示追加到末尾")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "track_type": "video",
                "index": -1
            }
        }


def handler(request: AddTrackRequest, task_manager: TaskManager):
    """创建轨道处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            track_id = task.jianyingProject.protocol.add_track(
                track_type=request.track_type,
                index=request.index
            )
            
            logger.info(f"创建轨道成功: task={request.task_id}, type={request.track_type}, track={track_id}")
            
            return success_response("轨道创建成功", {"track_id": track_id})
    except Exception as e:
        logger.error(f"创建轨道失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "创建轨道失败", {"error": str(e)})

