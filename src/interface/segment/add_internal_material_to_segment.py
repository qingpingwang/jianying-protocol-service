"""添加内部材质到片段接口（转场、动画等）"""
from pydantic import BaseModel, Field
from task_manager import TaskManager
from utils.models import *
from interface.utils import *
import logging

logger = logging.getLogger(__name__)


class AddInternalMaterialToSegmentRequest(BaseModel):
    """添加内部材质到片段请求"""
    task_id: str = Field(..., description="任务ID")
    segment_id: str = Field(..., description="片段ID")
    internal_material: JianYingInternalMaterialInfo = Field(..., description="内部材质信息（转场/动画）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-uuid",
                "segment_id": "segment-uuid",
                "internal_material": {
                    "material_info": {
                        "type": "transition",
                        "effect_id": "26135688",
                        "name": "推近 II",
                        "duration": 866666,
                        "is_overlap": True,
                        "category_id": "39663",
                        "category_name": "热门",
                        "path": "...",
                        "platform": "all",
                        "resource_id": "7290852476259930685"
                    }
                }
            }
        }


def handler(
    request: AddInternalMaterialToSegmentRequest, 
    task_manager: TaskManager
) -> dict:
    """添加内部材质到片段处理函数"""
    try:
        with task_manager.get_task(request.task_id) as task:
            if not task:
                return error_response(ErrorCode.NOT_FOUND, "任务不存在", {"task_id": request.task_id})
            
            material_id = task.jianyingProject.protocol.add_internal_material_to_segment(
                segment_id=request.segment_id,
                internal_material=request.internal_material
            )
            
            logger.info(f"添加内部材质成功: task={request.task_id}, segment={request.segment_id}, material={material_id}")
            
            return success_response("内部材质添加成功", {"material_id": material_id})
    except Exception as e:
        logger.error(f"添加内部材质失败: {e}", exc_info=True)
        return error_response(ErrorCode.INTERNAL_ERROR, "添加内部材质失败", {"error": str(e)})

