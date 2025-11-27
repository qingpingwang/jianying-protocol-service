"""创建任务接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from utils.models import JianYingBaseInfo
from interface.utils import success_response, error_response, ErrorCode
import logging

logger = logging.getLogger(__name__)


class CreateTaskRequest(BaseModel):
    """创建任务请求"""
    name: str = Field(..., description="项目名称", min_length=1, max_length=100)
    width: int = Field(720, description="画布宽度（像素）", ge=1, le=7680)
    height: int = Field(1280, description="画布高度（像素）", ge=1, le=4320)
    fps: int = Field(30, description="帧率（FPS）", ge=1, le=120)
    duration: int = Field(0, description="持续时间（秒）", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "我的项目",
                "width": 720,
                "height": 1280,
                "fps": 30,
                "duration": 10
            }
        }


def handler(
    request: CreateTaskRequest, 
    task_manager: TaskManager
) -> dict:
    """创建任务处理函数"""
    try:
        baseInfo = JianYingBaseInfo(
            name=request.name,
            width=request.width,
            height=request.height,
            fps=request.fps,
            duration=request.duration
        )
        
        task_id = task_manager.create_task(baseInfo)
        logger.info(f"创建任务成功: {task_id}")
        
        return success_response("任务创建成功", {"task_id": task_id})
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        return error_response(ErrorCode.INTERNAL_ERROR, "创建任务失败", {"error": str(e)})

