"""添加文本片段接口"""
from pydantic import BaseModel, Field
from typing import Optional
from task_manager import TaskManager
from utils.models import *
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class AddTextSegmentRequest(BaseModel):
    """添加文本片段请求"""
    task_id: str = Field(..., description="任务ID")
    track_id: str = Field(..., description="轨道ID")
    text_material: JianYingTextMaterialInfo = Field(..., description="文本素材信息")
    start_time: Optional[int] = Field(None, description="插入时间点（毫秒），None表示追加到轨道末尾")
    duration: int = Field(5000, description="文本显示时长（毫秒）", gt=0)
    transform: Optional[SegmentTransformInfo] = Field(None, description="变换信息（缩放、旋转、平移）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "track_id": "track-uuid",
                "start_time": 0,
                "duration": 5000,
                "text_material": {
                    "text": "默认文本",
                    "background_color": "#77157a",
                    "background_alpha": 1.0,
                    "styles": [
                        {
                            "bold": True,
                            "fill": {
                                "content": {
                                    "render_type": "solid",
                                    "solid": {
                                        "alpha": 1.0,
                                        "color": [1.0, 1.0, 1.0]
                                    }
                                }
                            },
                            "font": {
                                "id": "",
                                "path": "/Applications/VideoFusion-macOS.app/Contents/Resources/Font/SystemFont/zh-hans.ttf"
                            },
                            "range": [0, 4],
                            "size": 14.41,
                            "strokes": [],
                            "useLetterColor": True
                        }
                    ]
                },
                "transform": {
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                    "rotate": 0,
                    "translate_x": 0.0,
                    "translate_y": -0.6
                }
            }
        }


def handler(
    request: AddTextSegmentRequest, 
    task_manager: TaskManager
) -> dict:
    """添加文本片段处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            segment_id = task.jianyingProject.protocol.add_text_segment_to_track(
                track_id=request.track_id,
                text_material=request.text_material,
                start_time=request.start_time,
                duration=request.duration,
                transform_info=request.transform
            )
            
            logger.info(f"添加文本片段成功: task={request.task_id}, track={request.track_id}, segment={segment_id}")
            
            return success_response("文本片段添加成功", {"segment_id": segment_id})
    except Exception as e:
        logger.error(f"添加文本片段失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "添加文本片段失败", {"error": str(e)})

