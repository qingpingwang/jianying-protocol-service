"""
剪映协议服务器 - 入口文件

职责：
1. 应用初始化（日志、TaskManager）
2. 路由注册（映射到 interface 模块）
3. 全局异常处理
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from task_manager import TaskManager

# 导入接口公共工具
from interface.utils import BaseResponse, success_response, error_response

# 导入接口模块
from interface.task import *
from interface.track import *
from interface.segment import *


# ==================== 日志配置 ====================
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tmp')

class DailyRotatingFileHandler(logging.Handler):
    """按日期自动切换的日志处理器"""
    
    def __init__(self, log_dir: str, formatter: logging.Formatter):
        super().__init__()
        self.log_dir = log_dir
        self._formatter = formatter
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.current_date = None
        self.file_handler = None
        self._rotate_if_needed()
    
    def _rotate_if_needed(self):
        """检查是否需要切换日志文件"""
        today = datetime.now().strftime('%Y%m%d')
        
        if today != self.current_date:
            if self.file_handler:
                self.file_handler.close()
            
            log_filename = f"{today}.log"
            log_path = os.path.join(self.log_dir, log_filename)
            
            self.file_handler = logging.FileHandler(log_path, encoding='utf-8')
            self.file_handler.setFormatter(self._formatter)
            
            self.current_date = today
    
    def emit(self, record):
        """输出日志记录"""
        try:
            self._rotate_if_needed()
            self.file_handler.emit(record)
        except Exception:
            self.handleError(record)
    
    def close(self):
        """关闭处理器"""
        if self.file_handler:
            self.file_handler.close()
        super().close()

def setup_logging():
    """配置日志：按日期自动切换文件"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(filename)s:%(lineno)d - %(levelname)s: %(message)s'
    )
    
    file_handler = DailyRotatingFileHandler(LOG_DIR, formatter)
    root_logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    logger = logging.getLogger(__name__)
    today = datetime.now().strftime('%Y%m%d')
    logger.info(f"日志系统初始化完成，日志文件: {LOG_DIR}/{today}.log")
    return logger

logger = setup_logging()

# ==================== 全局变量 ====================
task_manager: TaskManager | None = None

# ==================== 生命周期管理 ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global task_manager
    logger.info("========== 服务启动 ==========")
    logger.info("初始化 TaskManager...")
    task_manager = TaskManager()
    logger.info("TaskManager 初始化完成")
    
    yield
    
    logger.info("========== 服务关闭 ==========")
    logger.info("清理资源...")

# ==================== FastAPI 应用 ====================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

app = FastAPI(
    title="剪映协议服务器",
    description="剪映草稿管理 HTTP API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not IS_PRODUCTION else None,
    redoc_url="/redoc" if not IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not IS_PRODUCTION else None
)


# ==================== 路由映射 ====================

@app.get("/", response_model=BaseResponse, tags=["系统"])
async def root():
    """根路径"""
    return success_response(
        message="剪映协议服务器",
        data={
            "service": "剪映协议服务器",
            "status": "running",
            "version": "1.0.0"
        }
    )

@app.get("/health", response_model=BaseResponse, tags=["系统"])
async def health():
    """健康检查"""
    return success_response(
        message="服务正常",
        data={
            "status": "healthy",
            "version": "1.0.0"
        }
    )

# ---------- 任务管理 ----------
@app.post("/tasks", response_model=BaseResponse, tags=["任务管理"])
async def api_create_task(request: create_task.CreateTaskRequest):
    """创建新任务"""
    return create_task.handler(request, task_manager)

@app.get("/tasks/{task_id}", response_model=BaseResponse, tags=["任务管理"])
async def api_get_task(task_id: str):
    """获取任务信息"""
    return get_task.handler(task_id, task_manager)

@app.delete("/tasks", response_model=BaseResponse, tags=["任务管理"])
async def api_remove_task(request: remove_task.RemoveTaskRequest):
    """删除任务"""
    return remove_task.handler(request, task_manager)

@app.post("/export", response_model=BaseResponse, tags=["任务管理"])
async def api_export_task(request: export_task.ExportTaskRequest):
    """导出任务到 OSS"""
    return export_task.handler(request, task_manager)

@app.get("/tasks/{task_id}/draft_info", response_model=BaseResponse, tags=["任务数据"])
async def api_get_draft_info(task_id: str):
    """获取草稿数据"""
    return get_draft_info.handler(task_id, task_manager)

@app.get("/tasks/{task_id}/draft_meta_info", response_model=BaseResponse, tags=["任务数据"])
async def api_get_draft_meta_info(task_id: str):
    """获取草稿元信息"""
    return get_draft_meta_info.handler(task_id, task_manager)

# ---------- 轨道管理 ----------
@app.post("/tracks", response_model=BaseResponse, tags=["轨道管理"])
async def api_add_track(request: add_track.AddTrackRequest):
    """创建轨道"""
    return add_track.handler(request, task_manager)

@app.delete("/tracks", response_model=BaseResponse, tags=["轨道管理"])
async def api_remove_track(request: remove_track.RemoveTrackRequest):
    """删除轨道"""
    return remove_track.handler(request, task_manager)

@app.get("/tasks/{task_id}/tracks", response_model=BaseResponse, tags=["轨道管理"])
async def api_get_tracks(task_id: str):
    """获取轨道列表"""
    return get_tracks.handler(task_id, task_manager)

@app.get("/tasks/{task_id}/tracks/count", response_model=BaseResponse, tags=["轨道管理"])
async def api_get_track_count(task_id: str):
    """获取轨道数量"""
    return get_track_count.handler(task_id, task_manager)

@app.get("/tasks/{task_id}/tracks/index/{index}", response_model=BaseResponse, tags=["轨道管理"])
async def api_get_track_by_index(task_id: str, index: int):
    """根据索引获取轨道"""
    return get_track_by_index.handler(task_id, index, task_manager)

@app.get("/tasks/{task_id}/tracks/{track_id}", response_model=BaseResponse, tags=["轨道管理"])
async def api_get_track(task_id: str, track_id: str):
    """获取轨道详情"""
    return get_track.handler(task_id, track_id, task_manager)

# ---------- 片段管理 ----------
@app.post("/segments/media", response_model=BaseResponse, tags=["片段管理"])
async def api_add_media_segment(request: add_media_segment.AddMediaSegmentRequest):
    """添加媒体片段（视频/图片/音频）"""
    return add_media_segment.handler(request, task_manager)

@app.post("/segments/text", response_model=BaseResponse, tags=["片段管理"])
async def api_add_text_segment(request: add_text_segment.AddTextSegmentRequest):
    """添加文本片段"""
    return add_text_segment.handler(request, task_manager)

@app.post("/segments/sticker", response_model=BaseResponse, tags=["片段管理"])
async def api_add_sticker_segment(request: add_sticker_segment.AddStickerSegmentRequest):
    """添加贴纸片段"""
    return add_sticker_segment.handler(request, task_manager)

@app.post("/segments/complex-text", response_model=BaseResponse, tags=["片段管理"])
async def api_add_complex_text_segment(request: add_complex_text_segment.AddComplexTextSegmentRequest):
    """添加复杂文本片段（带花字、气泡等特效）"""
    return add_complex_text_segment.handler(request, task_manager)

@app.post("/segments/filter", response_model=BaseResponse, tags=["片段管理"])
async def api_add_filter_segment(request: add_filter_segment.AddFilterSegmentRequest):
    """添加滤镜片段"""
    return add_filter_segment.handler(request, task_manager)

@app.post("/segments/effect", response_model=BaseResponse, tags=["片段管理"])
async def api_add_effect_segment(request: add_effect_segment.AddEffectSegmentRequest):
    """添加视频特效片段"""
    return add_effect_segment.handler(request, task_manager)

@app.post("/segments/audio-effect", response_model=BaseResponse, tags=["片段管理"])
async def api_add_audio_effect_segment(request: add_audio_effect_segment.AddAudioEffectSegmentRequest):
    """添加音效片段"""
    return add_audio_effect_segment.handler(request, task_manager)

@app.post("/segments/internal-material", response_model=BaseResponse, tags=["片段管理"])
async def api_add_internal_material_to_segment(request: add_internal_material_to_segment.AddInternalMaterialToSegmentRequest):
    """添加内部材质到片段（转场、动画等）"""
    return add_internal_material_to_segment.handler(request, task_manager)

@app.post("/segments/transform", response_model=BaseResponse, tags=["片段管理"])
async def api_update_segment_transform(request: update_segment_transform.UpdateSegmentTransformRequest):
    """更新片段变换信息（位置、缩放、旋转）"""
    return update_segment_transform.handler(request, task_manager)

@app.post("/segments/text-material", response_model=BaseResponse, tags=["片段管理"])
async def api_update_text_material(request: update_text_material.UpdateTextMaterialRequest):
    """更新文本片段的文本内容"""
    return update_text_material.handler(request, task_manager)

@app.post("/segments/adjust-info", response_model=BaseResponse, tags=["片段管理"])
async def api_update_adjust_info(request: update_adjust_info.UpdateAdjustInfoRequest):
    """更新视频片段的调色信息"""
    return update_adjust_info.handler(request, task_manager)

@app.delete("/segments", response_model=BaseResponse, tags=["片段管理"])
async def api_remove_segment(request: remove_segment.RemoveSegmentRequest):
    """删除片段"""
    return remove_segment.handler(request, task_manager)

@app.get("/tasks/{task_id}/tracks/{track_id}/segments/count", response_model=BaseResponse, tags=["片段管理"])
async def api_get_segment_count(task_id: str, track_id: str):
    """获取片段数量"""
    return get_segment_count.handler(task_id, track_id, task_manager)

@app.get("/tasks/{task_id}/tracks/{track_id}/segments/index/{index}", response_model=BaseResponse, tags=["片段管理"])
async def api_get_segment_by_index(task_id: str, track_id: str, index: int):
    """根据索引获取片段"""
    return get_segment_by_index.handler(task_id, track_id, index, task_manager)

# ==================== 错误处理 ====================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=error_response(
            code=500,
            message="内部服务器错误",
            data={"error": str(exc)}
        ).dict()
    )

# ==================== 启动入口 ====================
if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动服务器...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
