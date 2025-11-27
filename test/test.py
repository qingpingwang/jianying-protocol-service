import sys
import os
import shutil
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 将 src 目录添加到 Python 搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from task_manager import TaskManager
from utils.models import *
from utils.protocol_utils import JianYingProtocol
from utils.function_utils import get_project_path

# macOS 剪映工程目录
JIANYING_PROJECT_DIR = os.path.join(os.path.expanduser('~'), 'Movies/JianyingPro/User Data/Projects/com.lveditor.draft')


def copy_to_jianying(baseInfo: JianYingBaseInfo) -> str:
    """拷贝项目到剪映工程目录"""
    project_path = get_project_path(baseInfo.unique_id)
    jianying_project_path = os.path.join(JIANYING_PROJECT_DIR, baseInfo.name)
    if os.path.exists(jianying_project_path):
        shutil.rmtree(jianying_project_path)
    shutil.copytree(project_path, jianying_project_path)
    return jianying_project_path

def sticker_material_info() -> JianYingInternalMaterialInfo:
    material_info = {
        "aigc_type": None,
        "background_alpha": 1.0,
        "background_color": "",
        "border_color": "",
        "border_line_style": 0,
        "border_width": 0.0,
        "category_id": "10515",
        "category_name": "热门",
        "check_flag": 1,
        "combo_info": {
            "text_templates": []
        },
        "cycle_setting": True,
        "formula_id": "",
        "global_alpha": 1.0,
        "has_shadow": False,
        "icon_url": "https://p9-heycan-jy-sign.byteimg.com/tos-cn-i-3jr8j4ixpe/4c0f3e2ba22444faa97009d364b91116~tplv-3jr8j4ixpe-resize:200:200.png?x-expires=1782886265&x-signature=wt0luVbzOKaahZnED9azyyLtCLI%3D",
        "id": "077DEC43-6160-4E95-8142-966980FAFA71",
        "multi_language_current": None,
        "name": "红圈 圈重点",
        "original_size": [],
        "path": "/Users/beyond-today/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/artistEffect/7437023238108105995/26c8e890768185d01a62a63be1307aa5",
        "platform": "all",
        "preview_cover_url": "https://p9-heycan-jy-sign.byteimg.com/tos-cn-i-3jr8j4ixpe/4c0f3e2ba22444faa97009d364b91116~tplv-3jr8j4ixpe-resize:200:200.png?x-expires=1782886265&x-signature=wt0luVbzOKaahZnED9azyyLtCLI%3D",
        "radius": {
            "bottom_left": 0.0,
            "bottom_right": 0.0,
            "top_left": 0.0,
            "top_right": 0.0
        },
        "request_id": "202507011411054090DAF8422BF782CB7D",
        "resource_id": "7437023238108105995",
        "sequence_type": False,
        "shadow_alpha": 0.8,
        "shadow_angle": 0.0,
        "shadow_color": "",
        "shadow_distance": 0.0,
        "shadow_point": {
            "x": 0.0,
            "y": 0.0
        },
        "shadow_smoothing": 0.0,
        "shape_param": {
            "custom_points": [],
            "roundness": [],
            "shape_size": [],
            "shape_type": 0
        },
        "source_platform": 1,
        "sticker_id": "7437023238108105995",
        "sub_type": 0,
        "team_id": "",
        "type": "sticker",
        "unicode": ""
    }
    return JianYingInternalMaterialInfo(material_info=material_info)

def adjust_info() -> AdjustInfo:
    return AdjustInfo(vignetting=-15, temperature=30)

def transition_effect_info() -> JianYingInternalMaterialInfo:
    """推近 II 转场效果"""
    material_info = {
        "category_id": "39663",
        "category_name": "热门",
        "duration": 866666,
        "effect_id": "26135688",
        "id": "34EE7740-C510-4165-A8CD-C36AB99ADF6A",
        "is_overlap": True,
        "name": "推近 II",
        "path": "/Users/beyond-today/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/effect/26135688/94815943a86e741a5fec1737fbb46d60",
        "platform": "all",
        "request_id": "202506291624344CB1B5E1AB686C3140FC",
        "resource_id": "7290852476259930685",
        "type": "transition"
    }
    return JianYingInternalMaterialInfo(material_info=material_info)

def animation_effect_info() -> JianYingInternalMaterialInfo:
    """展开入场动画"""
    material_info = {
        "animations": [
            {
                "anim_adjust_params": None,
                "category_id": "in",
                "category_name": "入场",
                "duration": 500000,
                "id": "12088589",
                "material_type": "video",
                "name": "展开",
                "panel": "video",
                "path": "/Users/beyond-today/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/effect/12088589/1dddfd30d0529fb869d65bcdccb9f9bf",
                "platform": "all",
                "request_id": "20251124115610316A2F2282152272A69E",
                "resource_id": "7221413342257091133",
                "start": 0,
                "type": "in"
            }
        ],
        "id": "79B41FAC-C051-4CA3-B0ED-FB5797411EF5",
        "multi_language_current": "none",
        "type": "sticker_animation"
    }
    return JianYingInternalMaterialInfo(material_info=material_info)

def filter_material_info() -> JianYingInternalMaterialInfo:
    """高清增强滤镜"""
    material_info = {
        "adjust_params": [],
        "algorithm_artifact_path": "",
        "apply_target_type": 0,
        "bloom_params": None,
        "category_id": "10494",
        "category_name": "人像",
        "color_match_info": {
            "source_feature_path": "",
            "target_feature_path": "",
            "target_image_path": ""
        },
        "effect_id": "7426668776491453707",
        "enable_skin_tone_correction": False,
        "exclusion_group": [],
        "face_adjust_params": [],
        "formula_id": "",
        "id": "3CB3DEA4-74AD-4C7C-893C-A717DC183B22",
        "intensity_key": "",
        "multi_language_current": "",
        "name": "高清增强",
        "panel_id": "",
        "path": "/Users/beyond-today/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/artistEffect/7426668776491453707/c28d7683eb3bbc58cd3b008b380ed551",
        "platform": "all",
        "request_id": "20250701142236DCBEEA77AA61FB941FC4",
        "resource_id": "7426668776491453707",
        "source_platform": 1,
        "sub_type": "none",
        "time_range": None,
        "type": "filter",
        "value": 1.0,
        "version": ""
    }
    return JianYingInternalMaterialInfo(material_info=material_info)

def video_effect_material_info() -> JianYingInternalMaterialInfo:
    """放大镜视频特效"""
    material_info = {
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
    return JianYingInternalMaterialInfo(material_info=material_info)

def complex_text_material_info() -> JianYingTextComplexStyle:
    """复杂文本样式测试数据（从剪映导出的真实数据）"""
    complex_style_dict = {
        "text_segment": {
            "caption_info": None,
            "cartoon": False,
            "clip": {
                "alpha": 1.0,
                "flip": {"horizontal": False, "vertical": False},
                "rotation": 0.0,
                "scale": {"x": 1.0, "y": 1.0},
                "transform": {"x": 0.0, "y": -0.3272727272727274}
            },
            "common_keyframes": [],
            "enable_adjust": False,
            "enable_color_correct_adjust": False,
            "enable_color_curves": True,
            "enable_color_match_adjust": False,
            "enable_color_wheels": True,
            "enable_lut": False,
            "enable_smart_color_adjust": False,
            "extra_material_refs": [
                "AA463A1A-2BAD-468A-8889-36CDE483A01C",
                "998E8840-D546-4638-A56A-0A5936FA8573",
                "AAFAD0EB-C2FF-4A9C-9F84-2AC83CCB99A8",
                "998E8840-D546-4638-A56A-0A5936FA8573"
            ],
            "group_id": "",
            "hdr_settings": None,
            "id": "1631B100-625C-41CF-A30D-35AB47B98CC6",
            "intensifies_audio": False,
            "is_placeholder": False,
            "is_tone_modify": False,
            "keyframe_refs": [],
            "last_nonzero_volume": 1.0,
            "material_id": "897126D5-1A10-4CF6-9D5E-FC52F2409E3A",
            "render_index": 14000,
            "responsive_layout": {
                "enable": False,
                "horizontal_pos_layout": 0,
                "size_layout": 0,
                "target_follow": "",
                "vertical_pos_layout": 0
            },
            "reverse": False,
            "source_timerange": None,
            "speed": 1.0,
            "target_timerange": {"duration": 3000000, "start": 933333},
            "template_id": "",
            "template_scene": "default",
            "track_attribute": 0,
            "track_render_index": 1,
            "uniform_scale": {"on": True, "value": 1.0},
            "visible": True,
            "volume": 1.0
        },
        "materials": {
            "texts": [{
                "add_type": 0,
                "alignment": 1,
                "background_alpha": 1.0,
                "background_color": "",
                "background_height": 0.14,
                "background_horizontal_offset": 0.0,
                "background_round_radius": 0.0,
                "background_style": 0,
                "background_vertical_offset": 0.0,
                "background_width": 0.14,
                "base_content": "",
                "bold_width": 0.0,
                "border_alpha": 1.0,
                "border_color": "#000000",
                "border_width": 0.08,
                "caption_template_info": {
                    "category_id": "",
                    "category_name": "",
                    "effect_id": "",
                    "is_new": False,
                    "path": "",
                    "request_id": "",
                    "resource_id": "",
                    "resource_name": "",
                    "source_platform": 0
                },
                "check_flag": 7,
                "combo_info": {"text_templates": []},
                "content": "{\"styles\":[{\"fill\":{\"content\":{\"solid\":{\"color\":[1,1,1]}}},\"range\":[0,4],\"effectStyle\":{\"path\":\"/Users/beyond-today/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/artistEffect/6896137858998930701/6921e4f779070da71de81e8cac48f03c\",\"id\":\"6896137858998930701\"},\"size\":15,\"font\":{\"path\":\"/Applications/VideoFusion-macOS.app/Contents/Resources/Font/SystemFont/zh-hans.ttf\",\"id\":\"\"}}],\"text\":\"默认文本\"}",
                "fixed_height": -1.0,
                "fixed_width": -1.0,
                "font_category_id": "",
                "font_category_name": "",
                "font_id": "",
                "font_name": "",
                "font_path": "/Applications/VideoFusion-macOS.app/Contents/Resources/Font/SystemFont/zh-hans.ttf",
                "font_resource_id": "",
                "font_size": 15.0,
                "font_source_platform": 0,
                "font_team_id": "",
                "font_title": "none",
                "font_url": "",
                "fonts": [],
                "force_apply_line_max_width": False,
                "global_alpha": 1.0,
                "group_id": "",
                "has_shadow": False,
                "id": "897126D5-1A10-4CF6-9D5E-FC52F2409E3A",
                "initial_scale": 1.0,
                "inner_padding": -1.0,
                "is_rich_text": False,
                "italic_degree": 0,
                "ktv_color": "",
                "language": "",
                "layer_weight": 1,
                "letter_spacing": 0.0,
                "line_feed": 1,
                "line_max_width": 0.82,
                "line_spacing": 0.02,
                "multi_language_current": "none",
                "name": "",
                "original_size": [],
                "preset_category": "",
                "preset_category_id": "",
                "preset_has_set_alignment": False,
                "preset_id": "",
                "preset_index": 0,
                "preset_name": "",
                "recognize_task_id": "",
                "recognize_type": 0,
                "relevance_segment": [],
                "shadow_alpha": 0.9,
                "shadow_angle": -45.0,
                "shadow_color": "",
                "shadow_distance": 5.0,
                "shadow_point": {"x": 0.6363961030678928, "y": -0.6363961030678927},
                "shadow_smoothing": 0.45,
                "shape_clip_x": False,
                "shape_clip_y": False,
                "source_from": "",
                "style_name": "",
                "sub_type": 0,
                "subtitle_keywords": None,
                "subtitle_template_original_fontsize": 0.0,
                "text_alpha": 1.0,
                "text_color": "#FFFFFF",
                "text_curve": {"angle": 72.0, "enable": False},
                "text_preset_resource_id": "",
                "text_size": 30,
                "text_to_audio_ids": [],
                "tts_auto_update": False,
                "type": "text",
                "typesetting": 0,
                "underline": False,
                "underline_offset": 0.22,
                "underline_width": 0.05,
                "use_effect_default_color": True,
                "words": {"end_time": [], "start_time": [], "text": []}
            }],
            "text_templates": [],
            "material_animations": [{
                "animations": [{
                    "anim_adjust_params": None,
                    "category_id": "ruchang",
                    "category_name": "入场",
                    "duration": 500000,
                    "id": "3704299",
                    "material_type": "sticker",
                    "name": "向上弹入",
                    "panel": "",
                    "path": "/Users/beyond-today/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/effect/3704299/56dae21f3bf4915e783bde52578899bb",
                    "platform": "all",
                    "request_id": "20250814115407E483F0E1197720729851",
                    "resource_id": "7123116334677758501",
                    "start": 0,
                    "type": "in"
                }],
                "id": "AA463A1A-2BAD-468A-8889-36CDE483A01C",
                "multi_language_current": "none",
                "type": "sticker_animation"
            }],
            "effects": [
                {
                    "adjust_params": [],
                    "algorithm_artifact_path": "",
                    "apply_target_type": 0,
                    "bloom_params": None,
                    "category_id": "panel-text-flower",
                    "category_name": "花字",
                    "color_match_info": {
                        "source_feature_path": "",
                        "target_feature_path": "",
                        "target_image_path": ""
                    },
                    "effect_id": "6896137858998930701",
                    "enable_skin_tone_correction": False,
                    "exclusion_group": [],
                    "face_adjust_params": [],
                    "formula_id": "",
                    "id": "998E8840-D546-4638-A56A-0A5936FA8573",
                    "intensity_key": "",
                    "multi_language_current": "",
                    "name": "土酷红黄色花字",
                    "panel_id": "",
                    "path": "/Users/beyond-today/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/artistEffect/6896137858998930701/6921e4f779070da71de81e8cac48f03c",
                    "platform": "all",
                    "request_id": "202508141136370B682C96E85D20497DFF",
                    "resource_id": "6896137858998930701",
                    "source_platform": 1,
                    "sub_type": "none",
                    "time_range": None,
                    "type": "text_effect",
                    "value": 1.0,
                    "version": ""
                },
                {
                    "adjust_params": [],
                    "algorithm_artifact_path": "",
                    "apply_target_type": 0,
                    "bloom_params": None,
                    "category_id": "bubble",
                    "category_name": "气泡",
                    "color_match_info": {
                        "source_feature_path": "",
                        "target_feature_path": "",
                        "target_image_path": ""
                    },
                    "effect_id": "763868",
                    "enable_skin_tone_correction": False,
                    "exclusion_group": [],
                    "face_adjust_params": [],
                    "formula_id": "",
                    "id": "AAFAD0EB-C2FF-4A9C-9F84-2AC83CCB99A8",
                    "intensity_key": "",
                    "multi_language_current": "",
                    "name": "标题58",
                    "panel_id": "",
                    "path": "/Users/beyond-today/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro/User Data/Cache/effect/763868/c14ab15eacba7f80be940124dc05ccf7",
                    "platform": "all",
                    "request_id": "20250814113625976523A2013063C1FA5D",
                    "resource_id": "6838834553050632717",
                    "source_platform": 0,
                    "sub_type": "none",
                    "time_range": None,
                    "type": "text_shape",
                    "value": 1.0,
                    "version": ""
                }
            ]
        }
    }
    
    return JianYingTextComplexStyle(
        text="默认文本",
        complex_style_info=complex_style_dict
    )

# 测试处理函数
def process(protocol: JianYingProtocol) -> str:
    video_track_id = protocol.add_track('video')
    
    # 1. 视频片段
    video_material = JianYingMediaMaterialInfo(
        url='./data/test.mp4', 
        media_type='video', 
        speed=2.0, 
        category='测试文件夹', 
        adjust_info=adjust_info()
    )
    
    segment_id0 = protocol.add_media_segment_to_track(
        track_id=video_track_id, 
        media_material=video_material, 
        start_time=1000
    )
    
    # 1.1 给视频片段添加转场效果
    transition_effect = transition_effect_info()
    protocol.add_internal_material_to_segment(
        segment_id=segment_id0,
        internal_material=transition_effect
    )
    
    # 1.2 给视频片段添加入场动画
    animation_effect = animation_effect_info()
    protocol.add_internal_material_to_segment(
        segment_id=segment_id0,
        internal_material=animation_effect
    )
    
    # 2. 图片片段
    image_material = JianYingMediaMaterialInfo(
        url='./data/1.gif', 
        media_type='photo', 
        category='测试文件夹', 
        material_name='测试图片'
    )
    
    segment_id1 = protocol.add_media_segment_to_track(
        track_id=video_track_id, 
        media_material=image_material
    )
    
   
    
    # 3. 音频片段
    audio_track_id = protocol.add_track('audio')
    audio_material = JianYingMediaMaterialInfo(
        url='./data/test.mp3', 
        from_time=0, 
        to_time=10000, 
        media_type='audio', 
        category='测试文件夹', 
        material_name='测试音频'
    )
    
    segment_id2 = protocol.add_media_segment_to_track(
        track_id=audio_track_id, 
        media_material=audio_material, 
        start_time=10000
    )
    
    # 4. 文本片段
    text_track_id = protocol.add_track('text')
    text_transform_info = SegmentTransformInfo(
        scale_x=1.0, 
        scale_y=1.0, 
        rotate=0, 
        translate_x=0.0, 
        translate_y=-0.6
    )
    
    text_material = JianYingTextMaterialInfo(
        text='测试文本', 
        background_color='#FFFFFF', 
        background_alpha=0.5
    )
    
    segment_id3 = protocol.add_text_segment_to_track(
        track_id=text_track_id, 
        text_material=text_material, 
        start_time=10000, 
        duration=10000, 
        transform_info=text_transform_info
    )
    
    # 5. 贴纸片段
    sticker_track_id = protocol.add_track('sticker')
    sticker_material = sticker_material_info()
    
    segment_id4 = protocol.add_sticker_segment_to_track(
        track_id=sticker_track_id, 
        sticker_material=sticker_material, 
        start_time=10000, 
        duration=10000
    )
    
    # 6. 复杂文本片段
    complex_text_material = complex_text_material_info()
    segment_id5 = protocol.add_complex_text_segment_to_track(
        track_id=text_track_id, 
        complex_text_material=complex_text_material, 
        start_time=0, 
        duration=3000
    )
    
    # 7. 滤镜片段
    filter_track_id = protocol.add_track('filter')
    filter_material = filter_material_info()
    segment_id6 = protocol.add_filter_segment_to_track(
        track_id=filter_track_id,
        filter_material=filter_material,
        start_time=0,
        duration=10000
    )
    
    # 8. 视频特效片段
    effect_track_id = protocol.add_track('effect')
    effect_material = video_effect_material_info()
    segment_id7 = protocol.add_effect_segment_to_track(
        track_id=effect_track_id,
        effect_material=effect_material,
        start_time=0,
        duration=10000
    )
    
    return protocol


if __name__ == '__main__':
    # Environment variables are loaded from .env file at the top of this file
    # Make sure you have created a .env file based on env.example
    
    taskManager = TaskManager()
    baseInfo = JianYingBaseInfo(name='test', width=720, height=1280, fps=30, duration=0)
    task_id = taskManager.create_task(baseInfo)
    with taskManager.get_task(task_id) as task:
        protocol = task.jianyingProject.protocol
        if protocol:
            process(protocol)
            # 保存项目与拷贝项目到剪映工程目录
            task.jianyingProject.save()
            jianying_project_path = copy_to_jianying(protocol.base_info)
            print(f'拷贝项目到剪映工程目录: {jianying_project_path}')
