import os
import json
from dataclasses import dataclass
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from urllib.parse import unquote, urlparse
from utils.function_utils import *

# ==================== 数据结构定义 ====================

@dataclass
class JianYingBaseInfo:
    """剪映基础信息（纯数据，无业务逻辑）"""
    name: str
    width: int = 720
    height: int = 1280
    fps: int = 30
    duration: int = 5000  # 持续时间（毫秒）
    unique_id: str | None = None  # 唯一ID，None则自动生成

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
    
    @staticmethod
    def from_unique_id(unique_id: str) -> 'JianYingBaseInfo':
        """从unique_id创建实例，其他字段将从缓存加载"""
        return JianYingBaseInfo(name='', unique_id=unique_id)

@dataclass
class JianYingData:
    """剪映完整数据（纯数据容器）"""
    baseInfo: JianYingBaseInfo
    draft_info: dict
    draft_meta_info: dict
    draft_virtual_store: dict
    
class MediaClipInfo(BaseModel):
    """媒体片段裁剪信息"""
    left_top_x: int = Field(0, description="左上角X坐标", ge=0)
    left_top_y: int = Field(0, description="左上角Y坐标", ge=0)
    width: int = Field(0, description="裁剪宽度", ge=0)
    height: int = Field(0, description="裁剪高度", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "left_top_x": 100,
                "left_top_y": 100,
                "width": 500,
                "height": 500
            }
        }
        
class AdjustInfo(BaseModel):
    """调节信息"""
    """色温、色调、饱和度、亮度、对比度、高光、阴影、白色、黑色、光感、锐化、清晰、颗粒、褪色、暗角"""
    temperature: int = Field(0, description="色温v3", ge=-50, le=50)
    tone: int = Field(0, description="色调v3", ge=-50, le=50)
    saturation: int = Field(0, description="饱和度v1", ge=-50, le=50)
    brightness: int = Field(0, description="亮度v2", ge=-50, le=50)
    contrast: int = Field(0, description="对比度v3", ge=-50, le=50)
    highlight: int = Field(0, description="高光v3", ge=-50, le=50)
    shadow: int = Field(0, description="阴影v3", ge=-50, le=50)
    white: int = Field(0, description="白色", ge=-50, le=50)
    black: int = Field(0, description="黑色", ge=-50, le=50)
    light_sensation: int = Field(0, description="光感", ge=-50, le=50)
    sharpen: int = Field(0, description="锐化v1", ge=0, le=100)
    clear: int = Field(0, description="褪色", ge=0, le=100)
    particle: int = Field(0, description="颗粒v2", ge=0, le=100)
    fade: int = Field(0, description="褪色", ge=0, le=100)
    vignetting: int = Field(0, description="暗角v1", ge=-50, le=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 0,
                "tone": 0,
                "saturation": 0,
                "brightness": 0,
                "contrast": 0,
                "highlight": 0,
                "shadow": 0,
                "white": 0,
                "black": 0,
                "light_sensation": 0,
                "sharpen": 0,
                "clear": 0,
                "particle": 0,
                "fade": 0,
                "vignetting": 0
            }
        }
    

class SegmentTransformInfo(BaseModel):
    """片段变换信息"""
    scale_x: float = Field(1.0, description="X轴缩放比例", gt=0)
    scale_y: float = Field(1.0, description="Y轴缩放比例", gt=0)
    rotate: float = Field(0.0, description="旋转角度（度）")
    translate_x: float = Field(0.0, description="X轴平移（比例）,画布中心为0,0，y轴向上为正，范围-1到1")
    translate_y: float = Field(0.0, description="Y轴平移（比例）,画布中心为0,0，x轴向右为正，范围-1到1")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scale_x": 1.5,
                "scale_y": 1.5,
                "rotate": 45,
                "translate_x": 0.0,
                "translate_y": -0.6
            }
        }

class JianYingMediaMaterialInfo(BaseModel):
    """剪映媒体素材"""
    url: str = Field(..., description="媒体URL", min_length=1)
    media_type: str = Field("video", description="素材类型：video/photo/audio/oral/sticker")
    speed: float = Field(1.0, description="播放速度", ge=0.1, le=10.0)
    mute: bool = Field(False, description="是否静音")
    from_time: int = Field(0, description="裁剪开始时间（毫秒）", ge=0)
    to_time: int = Field(-1, description="裁剪结束时间（毫秒，-1表示到结尾）", ge=-1)
    width: int = Field(0, description="宽度", ge=0)
    height: int = Field(0, description="高度", ge=0)
    clip_info: Optional[MediaClipInfo] = Field(None, description="裁剪信息")
    adjust_info: Optional[AdjustInfo] = Field(None, description="调节信息")
    material_name: str = Field('', description="素材名称")
    category: str = Field('', description="素材分类")
    duration: Optional[int] = Field(5000, description="素材时长（毫秒）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/video.mp4",
                "type": "video",
                "speed": 1.0,
                "mute": False,
                "from_time": 0,
                "to_time": -1,
                "width": 1920,
                "height": 1080,
                "clip_info": {
                    "left_top_x": 100,
                    "left_top_y": 100,
                    "width": 500,
                    "height": 500
                },
                "material_name": "视频.mp4",
                "category": "我的素材",
                "duration": 10000
            }
        }
    
    @model_validator(mode='after')
    def set_defaults(self):
        # 自动设置 material_name
        if not self.material_name and self.url:
            parsed = urlparse(self.url)
            path = parsed.path if parsed.path else self.url
            self.material_name = os.path.basename(unquote(path))
        
        # 自动设置 duration
        if (self.duration is None or self.duration <= 0) and self.url:
            if self.media_type in ["video", "audio", "oral"]:
                self.duration = get_media_duration(self.url)
            else:
                self.duration = 5000
        return self
    
class JianYingInternalMaterialInfo(BaseModel):
    """剪映内部素材信息（用于贴纸、特效等复杂素材）"""
    material_info: dict = Field(..., description="内部素材信息")
    class Config:
        json_schema_extra = {
            "example": {
                "material_info": {
                    "adjust_params": [
                        {
                            "default_value": 1.0,
                            "name": "effects_adjust_color",
                            "value": 1.0
                        },
                        {
                            "default_value": 0.5,
                            "name": "effects_adjust_size",
                            "value": 0.5
                        },
                        {
                            "default_value": 1.0,
                            "name": "effects_adjust_intensity",
                            "value": 1.0
                        },
                        {
                            "default_value": 0.5,
                            "name": "effects_adjust_vertical_shift",
                            "value": 0.5
                        },
                        {
                            "default_value": 0.5,
                            "name": "effects_adjust_horizontal_shift",
                            "value": 0.5
                        }
                    ],
                    "algorithm_artifact_path": "",
                    "apply_target_type": 2,
                    "apply_time_range": None,
                    "category_id": "39654",
                    "category_name": "热门",
                    "common_keyframes": [],
                    "disable_effect_faces": [],
                    "effect_id": "1520514",
                    "formula_id": "",
                    "id": "B2FB5E17-46EE-4210-B686-A5C7C4E89278",
                    "name": "放大镜",
                    "path": "/Users/who/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/effect/1520514/5f89a973e9cea025690bdb37a293a959",
                    "platform": "all",
                    "render_index": 0,
                    "request_id": "2024112214353296DE127029298AFE4795",
                    "resource_id": "7051836120224502308",
                    "source_platform": 0,
                    "time_range": None,
                    "track_render_index": 0,
                    "type": "video_effect",
                    "value": 1.0,
                    "version": ""
                }
            }
        }
    
# ==================== 文本样式相关模型 ====================

class RGBColor(BaseModel):
    """通用颜色定义（RGB，范围 0.0-1.0）"""
    r: float = Field(..., ge=0.0, le=1.0, description="红色分量")
    g: float = Field(..., ge=0.0, le=1.0, description="绿色分量")
    b: float = Field(..., ge=0.0, le=1.0, description="蓝色分量")
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'RGBColor':
        """从十六进制颜色创建（如 #FF0000）"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
            
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return cls(r=r, g=g, b=b)
    
    @classmethod
    def from_int_rgb(cls, r: int, g: int, b: int) -> 'RGBColor':
        """从整数 RGB 值创建（0-255）"""
        return cls(r=r/255.0, g=g/255.0, b=b/255.0)
    
    def to_list(self) -> list[float]:
        """转换为剪映格式 [r, g, b]"""
        return [self.r, self.g, self.b]

class TextSolidColor(BaseModel):
    """纯色填充"""
    alpha: float = Field(1.0, ge=0.0, le=1.0, description="透明度")
    color: list[float] = Field(..., description="RGB颜色数组 [r, g, b]")

class TextColorContent(BaseModel):
    """颜色内容"""
    render_type: str = Field("solid", description="渲染类型")
    solid: TextSolidColor = Field(..., description="纯色定义")

class TextFill(BaseModel):
    """文字填充"""
    content: TextColorContent = Field(..., description="颜色内容")

class TextFont(BaseModel):
    """字体定义"""
    id: str = Field("", description="字体ID")
    path: str = Field(
        "/Applications/VideoFusion-macOS.app/Contents/Resources/Font/SystemFont/zh-hans.ttf",
        description="字体路径"
    )

class TextStroke(BaseModel):
    """文字描边"""
    alpha: float = Field(1.0, ge=0.0, le=1.0, description="描边透明度")
    content: TextColorContent = Field(..., description="描边颜色")
    width: float = Field(0.08, ge=0.0, description="描边宽度")

class TextStyle(BaseModel):
    """文本样式"""
    bold: bool = Field(False, description="是否粗体")
    fill: TextFill = Field(..., description="填充色")
    font: TextFont = Field(default_factory=TextFont, description="字体")
    range: list[int] = Field(..., description="样式应用范围 [start, end]")
    size: float = Field(14.41, ge=1.0, description="字体大小")
    strokes: list[TextStroke] = Field(default_factory=list, description="描边列表")
    useLetterColor: bool = Field(True, description="是否使用字母颜色")

class JianYingTextMaterialInfo(BaseModel):
    """剪映文本素材（完整协议格式）"""
    text: str = Field(..., description="文本内容", min_length=1)
    styles: Optional[list[TextStyle]] = Field(None, description="样式列表，None 时自动创建默认样式")
    background_color: Optional[str] = Field(None, description="背景颜色（十六进制）")
    background_alpha: float = Field(1.0, description="背景透明度")
    
    @staticmethod
    def _build_text_style(
        text: str,
        font_size: float = 14.41,
        text_color: str = "#000000",
        stroke_color: str = "#FFFFFF",
        stroke_width: float = 0.08,
        bold: bool = False,
        font_path: str = "/Applications/VideoFusion-macOS.app/Contents/Resources/Font/SystemFont/zh-hans.ttf"
    ) -> TextStyle:
        """
        构建文本样式（内部方法）
        
        Args:
            text: 文本内容（用于计算 range）
            font_size: 字体大小
            text_color: 文字颜色（十六进制，如 #000000）
            stroke_color: 描边颜色（十六进制，如 #FFFFFF）
            stroke_width: 描边宽度
            bold: 是否粗体
            font_path: 字体路径
            
        Returns:
            TextStyle 对象
        """
        text_rgb = RGBColor.from_hex(text_color)
        stroke_rgb = RGBColor.from_hex(stroke_color)
        
        return TextStyle(
            bold=bold,
            fill=TextFill(
                content=TextColorContent(
                    render_type="solid",
                    solid=TextSolidColor(
                        alpha=1.0,
                        color=text_rgb.to_list()
                    )
                )
            ),
            font=TextFont(id="", path=font_path),
            range=[0, len(text)],
            size=font_size,
            strokes=[
                TextStroke(
                    alpha=1.0,
                    content=TextColorContent(
                        render_type="solid",
                        solid=TextSolidColor(
                            alpha=1.0,
                            color=stroke_rgb.to_list()
                        )
                    ),
                    width=stroke_width
                )
            ],
            useLetterColor=True
        )
    
    @model_validator(mode='after')
    def set_default_styles(self):
        """自动创建默认样式"""
        if self.styles is None or len(self.styles) == 0:
            # 调用 _build_text_style 创建默认样式
            self.styles = [self._build_text_style(self.text)]
        return self
    
    @classmethod
    def create_simple(
        cls,
        text: str,
        font_size: float = 14.41,
        text_color: str = "#000000",
        stroke_color: str = "#FFFFFF",
        stroke_width: float = 0.08,
        bold: bool = False,
        font_path: str = "/Applications/VideoFusion-macOS.app/Contents/Resources/Font/SystemFont/zh-hans.ttf",
        background_color: str = "",
        background_alpha: float = 1.0
    ) -> 'JianYingTextMaterialInfo':
        """
        创建简单文本样式（便捷方法）
        
        Args:
            text: 文本内容
            font_size: 字体大小
            text_color: 文字颜色（十六进制，如 #000000）
            stroke_color: 描边颜色（十六进制，如 #FFFFFF）
            stroke_width: 描边宽度
            bold: 是否粗体
            font_path: 字体路径
        """
        # 调用 _build_text_style 创建样式
        style = cls._build_text_style(
            text=text,
            font_size=font_size,
            text_color=text_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            bold=bold,
            font_path=font_path
        )
        
        return cls(
            text=text, 
            styles=[style], 
            background_color=background_color,
            background_alpha=background_alpha
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "默认文本",
                "styles": [
                    {
                        "bold": True,
                        "fill": {
                            "content": {
                                "render_type": "solid",
                                "solid": {
                                    "alpha": 1.0,
                                    "color": [0.0, 0.0, 0.0]
                                }
                            }
                        },
                        "font": {
                            "id": "",
                            "path": (
                                "/Applications/VideoFusion-macOS.app/Contents/"
                                "Resources/Font/SystemFont/zh-hans.ttf"
                            )
                        },
                        "range": [0, 4],
                        "size": 14.41,
                        "strokes": [
                            {
                                "alpha": 1.0,
                                "content": {
                                    "render_type": "solid",
                                    "solid": {
                                        "alpha": 1.0,
                                        "color": [1.0, 1.0, 1.0]
                                    }
                                },
                                "width": 0.08
                            }
                        ],
                        "useLetterColor": True
                    }
                ]
            }
        }

# 剪映文本复杂样式
class JianYingTextComplexStyle(BaseModel):
    """剪映文本复杂样式"""
    text: str = Field(..., description="文本内容", min_length=1)
    complex_style_info: dict = Field(..., description="复杂样式信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "默认文本",
                "complex_style_info": {}
            }
        }