import os
from urllib.parse import urlparse, unquote
import logging
import json
import hashlib
import uuid
import subprocess
logger = logging.getLogger(__name__)

# 缓存目录（绝对路径）
CACHE_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        '..', '..', 'tmp', 'jianying_project'
    )
)


# ==================== 工具函数 ====================

def get_file_extension(path: str) -> str:
    """
    获取文件扩展名
    """
    return os.path.splitext(path)[1].lower()

def get_material_type_by_extension(path: str) -> str:
    """
    根据文件扩展名判断素材类型
    
    Args:
        path: 文件路径或 URL
    
    Returns:
        素材类型: 'gif', 'photo', 'video'
    """
    ext = get_file_extension(path)
    
    if ext == '.gif':
        return 'gif'
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp']:
        return 'photo'
    else:
        return 'video'

def get_media_duration(media_path: str) -> int:
    """
    使用 ffprobe 获取音视频时长（毫秒）
    
    统一处理音频和视频文件，支持本地文件和 URL。
    
    Args:
        media_path: 媒体文件路径（本地路径或 URL）
    
    Returns:
        时长（毫秒），失败返回 0
    
    Raises:
        Exception: 当 ffprobe 执行失败、超时或输出无法解析时
    """
    import tempfile
    from utils.oss_utils import OssMixin
    
    temp_path = None
    try:
        # 如果是 URL，先下载到临时文件
        if media_path.startswith('http://') or media_path.startswith('https://'):
            oss = OssMixin()
            with tempfile.NamedTemporaryFile(suffix=get_file_extension(media_path), delete=False) as tmp_file:
                temp_path = tmp_file.name
            oss.get_object_file(media_path, temp_path)
            target_path = temp_path
        else:
            target_path = media_path
        
        # 使用 ffprobe 获取时长
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            target_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise Exception(f"ffprobe failed - exit code: {result.returncode}, error: {result.stderr}")
        
        data = json.loads(result.stdout)
        duration = int(float(data['format']['duration']) * 1000)
        
        logger.info(f"Media duration: {media_path} -> {duration}ms")
        return duration
        
    except subprocess.TimeoutExpired:
        logger.error(f"ffprobe timeout (10s) - {media_path}")
        raise Exception(f"ffprobe timeout (10s) - {media_path}")
    except json.JSONDecodeError as e:
        logger.error(f"ffprobe JSON parse failed: {e}, output: {result.stdout}")
        raise Exception(f"ffprobe JSON parse failed: {e}, output: {result.stdout}")
    except Exception as e:
        logger.error(f"Get media duration failed: {media_path}, {e}")
        raise
    finally:
        # 清理临时文件
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {temp_path}, {e}")
    
def load_json_data(path: str) -> dict:
    """加载 JSON 文件，失败时抛出异常"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e
    
def get_project_path(unique_id: str) -> str:
    """获取工程目录路径"""
    return os.path.join(CACHE_DIR, unique_id)

def get_resource_path(unique_id: str) -> str:
    """获取资源目录路径"""
    return os.path.join(get_project_path(unique_id), 'Resources')

def get_draft_path(project_path: str) -> str:
    """获取 draft_info.json 路径"""
    return os.path.join(project_path, 'draft_info.json')

def get_draft_meta_info_path(project_path: str) -> str:
    """获取 draft_meta_info.json 路径"""
    return os.path.join(project_path, 'draft_meta_info.json')

def get_draft_virtual_store_path(project_path: str) -> str:
    """获取 draft_virtual_store.json 路径"""
    return os.path.join(project_path, 'draft_virtual_store.json')

def url_to_filename(url: str) -> str:
    """URL → 唯一文件名 (name_hash.ext)"""
    decoded_url = unquote(url)
    parsed = urlparse(decoded_url)
    basename = os.path.basename(parsed.path)
    name, ext = os.path.splitext(basename)
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{url_hash}_{name}{ext}"

def build_draft_info(
    unique_id: str, 
    width: int, 
    height: int, 
    duration: int, 
    fps: int
) -> dict:
    return {
            'canvas_config': {
                'width': width,
                'height': height,
                'ratio': 'custom'
            },
            'duration': duration,
            'render_index_track_mode_on': True,
            'config': {'maintrack_adsorb': False},
            'color_space': 0,
            'fps': fps,
            'id': unique_id,
            'materials': {
                'videos': [],
                'texts': [],
                'audios': [],
                'stickers': [],
                'speeds': [],
                'effects': [],
                'video_effects': [],
                'placeholders': [],
                'transitions': [],
                'material_animations': []
            },
            'tracks': []
        }

def build_draft_meta_info(name: str) -> dict:
    return {
        'draft_materials': [{'type': 0, 'value': []}],
        'draft_name': name,
    }
        
def build_draft_virtual_store() -> dict:
    root_folder = build_folder_info('', 0)
    root_folder['id'] = ''
    return {
        'draft_materials': [],
        'draft_virtual_store': [
            {'type': 0, 'value': [root_folder]},
            {'type': 1, 'value': []},
            {'type': 2, 'value': []}
        ]
    }

def build_track(track_type: str) -> dict:
    return {
        'id': str(uuid.uuid4()),
        'name': '',
        'is_default_name': True,
        'type': track_type,
        'segments': []
    }
    
def build_speed(speed: float) -> dict:
    return {
        'curve_speed': None,
        'mode': 0,
        'speed': speed,
        'type': 'speed'
    }

def build_media_segment(
    material_id: str, 
    offset_time: int, 
    from_time: int, 
    duration: int, 
    speed: float, 
    volume: float = 1.0
) -> dict:
    return {
        'material_id': material_id,
        'target_timerange': {
            'start': offset_time,
            'duration': duration
        },
        'source_timerange': {
            'start': from_time,
            'duration': int(duration * speed)
        },
        'speed': speed,
        'reverse': False,
        'visible': True,
        'volume': volume,
        'extra_material_refs': []
    }
    
def build_segmen_no_source(
    material_id: str, 
    offset_time: int, 
    duration: int, 
) -> dict:
    return {
        'material_id': material_id,
        'source_timerange': None,
        'target_timerange': {
            'start': offset_time,
            'duration': duration
        },
        'visible': True,
    }
    
def build_crop_info(top_x, top_y, width, height):
    """
    将 MediaClipInfo 转换为剪映裁剪信息
    
    MediaClipInfo: (left_top_x, left_top_y) + (width, height)
    裁剪信息: 四个角的坐标（左上、右上、左下、右下）
    """
    left = top_x
    top = top_y
    right = left + width
    bottom = top + height
    
    return {
        'upper_left_x': left,      # 左上角 X
        'upper_left_y': top,       # 左上角 Y
        'upper_right_x': right,    # 右上角 X
        'upper_right_y': top,      # 右上角 Y
        'lower_left_x': left,      # 左下角 X
        'lower_left_y': bottom,    # 左下角 Y
        'lower_right_x': right,    # 右下角 X
        'lower_right_y': bottom    # 右下角 Y
    }
    
def build_folder_info(folder_name: str, timestamp: int | None = None) -> dict:
    import time
    time_now = int(time.time())
    ts = timestamp if timestamp else time_now
    ts_us = timestamp if timestamp else int(ts * 1000000)
    return {
        'creation_time': ts,
        'display_name': folder_name,
        'filter_type': 0,
        'id': str(uuid.uuid4()),
        'import_time': ts,
        'import_time_us': ts_us,
        'sort_sub_type': 0,
        'sort_type': 0
    }
    
def build_material_meta_info(
    extra_info: str, 
    file_path: str, 
    remote_url: str, 
    duration: int, 
    material_type: str, 
    width: int = 0, 
    height: int = 0
) -> dict:
    import time
    ts = int(time.time())
    ts_ms = int(time.time() * 1000000)
    return {
        'create_time': ts,
        'duration': duration * 1000,
        'extra_info': extra_info,
        'file_Path': file_path,
        'height': height,
        'import_time': ts,
        'import_time_ms': ts_ms,
        'metetype': material_type,
        'type': 0,
        'width': width,
        'remote_url': remote_url
    }
    
# 构建视频或图片素材
def build_video_or_photo_material(
    url: str, 
    path: str, 
    width: int, 
    height: int, 
    name: str
) -> dict:
    return {
        'remote_url': url,
        'path': path,
        'width': width,
        'height': height,
        'material_name': name,
        'category_name': 'local',
        'type': get_material_type_by_extension(url)
    }
    
def build_audio_material(
    url: str, 
    path: str, 
    name: str, 
    is_sound: bool = False
) -> dict:
    return {
        'remote_url': url,
        'path': path,
        'material_name': name,
        'category_name': 'local',
        'type': 'sound' if is_sound else 'extract_music'
    }
    
def build_text_material(
    text: str, 
    content: str, 
    background_color: str|None = None, 
    background_alpha: float = 1.0
) -> dict:
    text_material = {
        'type': 'text',
        'text': text,
        'alignment': 1,
        'content': content
    }
    if background_color:
        text_material['background_color'] = background_color
        text_material['background_color_alpha'] = background_alpha
        text_material['background_height'] = 0.14
        text_material['background_width'] = 0.14
        text_material['background_horizontal_offset'] = 0.0
        text_material['background_vertical_offset'] = 0.0
        text_material['background_round_radius'] = 0.3
        text_material['background_style'] = 1
        text_material['check_flag'] = 23
    return text_material

def build_adjust_material(value: float, type: str, version: str) -> dict:
    return {
        'type': type,
        'value': value,
        'path': "/Applications/VideoFusion-macOS.app/Contents/Resources/DefaultAdjustBundle/combine_adjust",
        'version': version,
    }

def normalize_adjust_value(value: int, ge: int, le: int) -> float:
    """
    归一化调节参数值
    
    Args:
        value: 原始值
        ge: 最小值（Field 的 ge 属性）
        le: 最大值（Field 的 le 属性）
        
    Returns:
        归一化后的浮点数
    """
    if ge < 0:
        # 双向调节（如色温 -50~50）：归一化到 -1.0 ~ 1.0
        # 例如 -15 / 50 = -0.3
        if le == 0: return 0.0
        return float(value) / float(le)
    else:
        # 单向调节（如锐化 0~100）：归一化到 0.0 ~ 1.0
        # 例如 50 / 100 = 0.5
        diff = float(le - ge)
        if diff == 0: return 0.0
        return float(value - ge) / diff

def write_json_file(data: dict, path: str):
    """
    原子写入 JSON 文件 - 防止数据损坏
    
    使用临时文件 + 原子重命名模式，确保：
    1. 写入过程中崩溃不会损坏原文件
    2. 多进程不会产生竞争
    3. 断电时数据已落盘
    """
    import tempfile
    
    # 在同一目录创建临时文件（确保在同一文件系统）
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_', suffix='.json')
    
    try:
        # 写入临时文件
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())  # 强制刷新到磁盘
        
        # 原子重命名（POSIX 保证原子性）
        os.replace(tmp_path, path)
    except Exception as e:
        # 失败时清理临时文件
        try:
            os.unlink(tmp_path)
        except:
            pass
        raise e