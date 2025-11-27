"""更新文本素材信息接口"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from utils.models import JianYingTextMaterialInfo
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class UpdateTextMaterialRequest(BaseModel):
    """更新文本素材信息请求"""
    task_id: str = Field(..., description="任务ID")
    segment_id: str = Field(..., description="文本片段ID")
    text_material: JianYingTextMaterialInfo = Field(..., description="文本素材信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "segment_id": "segment-uuid",
                "text_material": {
                    "text": "新的文本内容",
                    "font_path": "",
                    "font_size": 24,
                    "color": {
                        "r": 255,
                        "g": 255,
                        "b": 255
                    },
                    "background_color": "",
                    "background_alpha": 0.0
                }
            }
        }


def handler(
    request: UpdateTextMaterialRequest,
    task_manager: TaskManager
) -> dict:
    """更新文本素材信息处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"Task not found: {request.task_id}"
                )
            
            # 更新文本素材信息
            segment_id = task.jianyingProject.protocol.update_text_material_info(
                segment_id=request.segment_id,
                text_material=request.text_material
            )
            
            return success_response({
                "segment_id": segment_id,
                "message": "Text material updated successfully"
            })
            
    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return error_response(ErrorCode.VALIDATION_ERROR, str(e))
    except Exception as e:
        logger.error(f"Update text material failed: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, str(e))

