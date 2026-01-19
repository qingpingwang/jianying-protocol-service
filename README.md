# 剪映协议服务 (JianYing Protocol Service)

> 一个用于程序化创建和管理剪映草稿项目的 HTTP API 服务
> [剪映agent](https://wangqingping.top/resume)

## 📖 项目简介

剪映协议服务是一个基于 FastAPI 的 HTTP 服务，提供了完整的剪映草稿项目操作接口。通过本服务，你可以通过编程方式创建视频项目、添加素材、应用特效，无需手动使用剪映客户端。

### 核心特性

- ✅ **完整的草稿管理** - 创建、导出、查询剪映项目
- ✅ **轨道操作** - 支持视频、音频、文本、贴纸、特效、滤镜轨道
- ✅ **素材管理** - 视频、图片、音频、文本、贴纸等多种素材类型
- ✅ **特效系统** - 转场、动画、滤镜、视频特效
- ✅ **复杂文本** - 支持花字、气泡等复杂文本样式
- ✅ **OSS 集成** - 自动从阿里云 OSS 下载素材
- ✅ **RESTful API** - 标准 HTTP 接口，易于集成

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 阿里云 OSS 访问密钥 (可选，用于自动下载媒体资源)

### 安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
# 复制配置文件模板
cp env.example .env

# 3. 编辑 .env 文件，填入你的配置
# OSS_AK=your_access_key
# OSS_SK=your_secret_key
# PROJECT_REMOTE_PATH=https://your-oss-domain/path
```

**环境变量说明：**

- `OSS_AK` - 阿里云 OSS Access Key
- `OSS_SK` - 阿里云 OSS Secret Key
- `PROJECT_REMOTE_PATH` - 项目远程存储路径

> ⚠️ 注意：`.env` 文件包含敏感信息，已自动添加到 `.gitignore`，不会被提交到代码库

### 启动服务

```bash
# 开发模式
python src/main.py

# 或使用脚本
./start.sh
```

服务将在 `http://localhost:8000` 启动，访问 `http://localhost:8000/docs` 查看 API 文档。

## 📚 API 文档

### 系统接口


| 接口      | 方法 | 说明     |
| --------- | ---- | -------- |
| `/`       | GET  | 服务信息 |
| `/health` | GET  | 健康检查 |

### 任务管理


| 接口                               | 方法 | 说明           |
| ---------------------------------- | ---- | -------------- |
| `/tasks`                           | POST | 创建新任务     |
| `/tasks/{task_id}`                 | GET  | 获取任务信息   |
| `/export`                          | POST | 导出任务到 OSS |
| `/tasks/{task_id}/draft_info`      | GET  | 获取草稿数据   |
| `/tasks/{task_id}/draft_meta_info` | GET  | 获取草稿元信息 |

### 轨道管理


| 接口                                    | 方法   | 说明           |
| --------------------------------------- | ------ | -------------- |
| `/tracks`                               | POST   | 创建轨道       |
| `/tracks`                               | DELETE | 删除轨道       |
| `/tasks/{task_id}/tracks`               | GET    | 获取所有轨道   |
| `/tasks/{task_id}/tracks/{track_id}`    | GET    | 获取指定轨道   |
| `/tasks/{task_id}/tracks/count`         | GET    | 获取轨道数量   |
| `/tasks/{task_id}/tracks/index/{index}` | GET    | 按索引获取轨道 |

**支持的轨道类型：**

- `video` - 视频轨道
- `audio` - 音频轨道
- `text` - 文本轨道
- `sticker` - 贴纸轨道
- `effect` - 特效轨道
- `filter` - 滤镜轨道

### 片段管理


| 接口                                                        | 方法   | 说明                           |
| ----------------------------------------------------------- | ------ | ------------------------------ |
| `/segments/media`                                           | POST   | 添加媒体片段（视频/图片/音频） |
| `/segments/text`                                            | POST   | 添加文本片段                   |
| `/segments/sticker`                                         | POST   | 添加贴纸片段                   |
| `/segments/complex-text`                                    | POST   | 添加复杂文本片段               |
| `/segments/filter`                                          | POST   | 添加滤镜片段                   |
| `/segments/effect`                                          | POST   | 添加视频特效片段               |
| `/segments/internal-material`                               | POST   | 添加内部材质（转场/动画）      |
| `/segments/transform`                                       | POST   | 更新片段变换信息               |
| `/segments/text-material`                                   | POST   | 更新文本内容和样式             |
| `/segments/adjust-info`                                     | POST   | 更新色彩调节参数               |
| `/segments`                                                 | DELETE | 删除片段                       |
| `/tasks/{task_id}/tracks/{track_id}/segments/count`         | GET    | 获取片段数量                   |
| `/tasks/{task_id}/tracks/{track_id}/segments/index/{index}` | GET    | 按索引获取片段                 |

## 💡 使用示例

### 1. 创建基础视频项目

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 创建任务
response = requests.post(f"{BASE_URL}/tasks", json={
    "name": "我的视频项目",
    "width": 720,
    "height": 1280,
    "fps": 30
})
task_id = response.json()["data"]["task_id"]

# 2. 创建视频轨道
response = requests.post(f"{BASE_URL}/tracks", json={
    "task_id": task_id,
    "track_type": "video"
})
track_id = response.json()["data"]["track_id"]

# 3. 添加视频片段
requests.post(f"{BASE_URL}/segments/media", json={
    "task_id": task_id,
    "track_id": track_id,
    "media_material": {
        "url": "https://example.com/video.mp4",
        "media_type": "video",
        "speed": 1.0
    }
})

# 4. 导出项目
requests.post(f"{BASE_URL}/export", json={
    "task_id": task_id
})
```

### 2. 添加文本和特效

```python
# 创建文本轨道
response = requests.post(f"{BASE_URL}/tracks", json={
    "task_id": task_id,
    "track_type": "text"
})
text_track_id = response.json()["data"]["track_id"]

# 添加文本片段
requests.post(f"{BASE_URL}/segments/text", json={
    "task_id": task_id,
    "track_id": text_track_id,
    "text_material": {
        "text": "Hello World"
    },
    "duration": 5000,
    "transform": {
        "translate_y": -0.6
    }
})

# 创建滤镜轨道
response = requests.post(f"{BASE_URL}/tracks", json={
    "task_id": task_id,
    "track_type": "filter"
})
filter_track_id = response.json()["data"]["track_id"]

# 添加滤镜
requests.post(f"{BASE_URL}/segments/filter", json={
    "task_id": task_id,
    "track_id": filter_track_id,
    "filter_material": {
        "material_info": {
            "type": "filter",
            "name": "高清增强"
        }
    },
    "duration": 10000
})
```

## 🧪 测试

### 运行测试

```bash
python test/test.py
```

### 测试用例说明

测试文件 `test/test.py` 包含完整的功能演示：

#### 1. 视频片段测试 (`segment_id0`)

```python
video_material = JianYingMediaMaterialInfo(
    url='https://example.com/video.mp4',
    media_type='video',
    speed=2.0,  # 2倍速
    adjust_info=adjust_info()  # 调节信息（色温、亮度等）
)
```

- 支持倍速播放
- 支持色彩调节（色温、饱和度、亮度等）
- 自动添加转场和入场动画

#### 2. 图片片段测试 (`segment_id1`)

```python
image_material = JianYingMediaMaterialInfo(
    url='https://example.com/image.gif',
    media_type='photo'
)
```

- 支持静态图片和 GIF

#### 3. 音频片段测试 (`segment_id2`)

```python
audio_material = JianYingMediaMaterialInfo(
    url='https://example.com/audio.mp3',
    from_time=0,
    to_time=10000,  # 裁剪前 10 秒
    media_type='audio'
)
```

- 支持音频裁剪
- 自动检测时长

#### 4. 文本片段测试 (`segment_id3`)

```python
text_material = JianYingTextMaterialInfo(
    text='测试文本',
    background_color='#FFFFFF',
    background_alpha=0.5
)
```

- 支持文本样式定制
- 支持背景色和透明度

#### 5. 贴纸片段测试 (`segment_id4`)

- 使用剪映内置贴纸

#### 6. 复杂文本测试 (`segment_id5`)

- 支持花字特效
- 支持气泡样式
- 支持入场动画

#### 7. 滤镜测试 (`segment_id6`)

- 高清增强滤镜

#### 8. 视频特效测试 (`segment_id7`)

- 放大镜特效

### 辅助函数说明

#### `adjust_info()` - 色彩调节

支持的调节参数：

- `temperature` - 色温 (-50 ~ 50)
- `tone` - 色调 (-50 ~ 50)
- `saturation` - 饱和度 (-50 ~ 50)
- `brightness` - 亮度 (-50 ~ 50)
- `contrast` - 对比度 (-50 ~ 50)
- `highlight` - 高光 (-50 ~ 50)
- `shadow` - 阴影 (-50 ~ 50)
- `vignetting` - 暗角 (-50 ~ 50)

#### 其他辅助函数

- `sticker_material_info()` - 贴纸素材
- `transition_effect_info()` - "推近 II" 转场效果
- `animation_effect_info()` - "展开" 入场动画
- `filter_material_info()` - "高清增强" 滤镜
- `video_effect_material_info()` - "放大镜" 视频特效
- `complex_text_material_info()` - 带花字、气泡和动画的复杂文本

## 🏗️ 项目结构

```
jy-protocol-server/
├── src/
│   ├── interface/          # HTTP 接口层
│   │   ├── task/          # 任务管理接口
│   │   ├── track/         # 轨道管理接口
│   │   └── segment/       # 片段管理接口
│   ├── utils/             # 工具模块
│   │   ├── protocol_utils.py    # 协议处理核心
│   │   ├── models.py           # 数据模型
│   │   ├── function_utils.py    # 辅助函数
│   │   ├── complex_text.py     # 复杂文本处理
│   │   └── oss_utils.py         # OSS 工具
│   ├── jianying_project.py # 项目管理
│   ├── task_manager.py     # 任务管理器
│   └── main.py            # 服务入口
├── test/
│   └── test.py            # 功能测试
├── tmp/                   # 临时文件/日志
├── requirements.txt       # 依赖列表
└── README.md             # 本文档
```

## 🔧 核心架构

### 分层设计

```
┌─────────────────────────────────────┐
│     HTTP API Layer (FastAPI)        │  接口层
├─────────────────────────────────────┤
│     Business Logic Layer            │  业务层
│  - TaskManager                      │
│  - JianYingProject                  │
├─────────────────────────────────────┤
│     Protocol Layer                  │  协议层
│  - JianYingProtocol                 │
│  - Segment/Track/Material Handlers  │
├─────────────────────────────────────┤
│     Infrastructure Layer            │  基础层
│  - OSS Integration                  │
│  - File Management                  │
│  - Utils & Helpers                  │
└─────────────────────────────────────┘
```

### 关键类说明

#### `JianYingProtocol`

核心协议处理器，负责所有剪映草稿操作。

**主要方法：**

- `add_track()` - 添加轨道
- `add_media_segment_to_track()` - 添加媒体片段
- `add_text_segment_to_track()` - 添加文本片段
- `add_sticker_segment_to_track()` - 添加贴纸片段
- `add_filter_segment_to_track()` - 添加滤镜片段
- `add_effect_segment_to_track()` - 添加视频特效片段
- `add_complex_text_segment_to_track()` - 添加复杂文本片段
- `add_internal_material_to_segment()` - 添加转场/动画

#### `TaskManager`

任务生命周期管理器。

**特性：**

- 线程安全
- 自动落盘
- 闲置清理（60秒）
- 上下文管理器支持

#### `JianYingProject`

项目封装类，提供统一的项目操作接口。

## ⚙️ 配置说明

### 轨道类型配置

```python
JIANYING_TRACK_TYPES = [
    'audio', 'video', 'effect', 'filter', 
    'text', 'sticker', 'adjust'
]
```

### 素材类型配置

```python
JIANYING_MATERIAL_TYPES = [
    'videos', 'texts', 'audios', 'stickers', 
    'effects', 'video_effects', 'placeholders', 
    'transitions', 'material_animations', 'speeds'
]
```

### 片段类型配置

```python
SEGMENT_TYPE_CONFIG = {
    'sticker': {
        'material_type': 'stickers',
        'track_type': 'sticker',
        'required_material_type': 'sticker',
        'support_transform': True,
        'log_name': 'Sticker'
    },
    # ... 其他类型
}
```

## 📊 数据模型

### JianYingBaseInfo

```python
@dataclass
class JianYingBaseInfo:
    name: str                # 项目名称
    width: int = 720         # 画布宽度
    height: int = 1280       # 画布高度
    fps: int = 30            # 帧率
    duration: int = 0        # 持续时间（秒）
    unique_id: str = None    # 唯一ID
```

### JianYingMediaMaterialInfo

```python
class JianYingMediaMaterialInfo(BaseModel):
    url: str                      # 媒体URL
    media_type: str               # video/photo/audio/oral
    speed: float = 1.0            # 播放速度
    mute: bool = False            # 是否静音
    from_time: int = 0            # 裁剪开始（毫秒）
    to_time: int = -1             # 裁剪结束（毫秒）
    clip_info: MediaClipInfo      # 画面裁剪
    adjust_info: AdjustInfo       # 色彩调节
```

### SegmentTransformInfo

```python
class SegmentTransformInfo(BaseModel):
    scale_x: float = 1.0          # X轴缩放
    scale_y: float = 1.0          # Y轴缩放
    rotate: float = 0.0           # 旋转角度
    translate_x: float = 0.0      # X轴平移（-1~1）
    translate_y: float = 0.0      # Y轴平移（-1~1）
```

## 🔒 最佳实践

### 1. 使用上下文管理器

```python
with task_manager.get_task(task_id) as task:
    protocol = task.jianyingProject.protocol
    # 操作会自动保存
```

### 2. 错误处理

```python
try:
    segment_id = protocol.add_media_segment_to_track(...)
except ValueError as e:
    logger.error(f"Failed to add segment: {e}")
```

### 3. 资源管理

- 使用完毕后及时调用 `export` 导出项目
- 服务器会自动清理超过 60 秒未使用的任务

### 4. 性能优化

- 大量操作时使用批量接口
- 合理设置 OSS 缓存
- 控制并发任务数量

## 🐛 故障排查

### 常见问题

**Q: 提示 "Track not found"**
A: 确保先创建轨道，再添加片段。

**Q: 视频无法下载**
A: 检查 OSS 配置和网络连接，确保 `.env` 文件中的 `OSS_AK` 和 `OSS_SK` 配置正确。

**Q: 片段时长计算错误**
A: 确保视频 URL 可访问，服务器需要读取视频元信息。

**Q: 复杂文本不生效**
A: 检查 `complex_style_info` 结构是否完整，参考测试用例。

### 日志查看

日志文件位于 `tmp/` 目录，按日期自动切换：
