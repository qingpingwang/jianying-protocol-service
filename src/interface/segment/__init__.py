"""片段管理接口模块"""
from . import (
    add_media_segment,
    add_text_segment,
    add_sticker_segment,
    add_complex_text_segment,
    add_filter_segment,
    add_effect_segment,
    add_audio_effect_segment,
    add_internal_material_to_segment,
    update_segment_transform,
    update_text_material,
    update_text_content,
    update_adjust_info,
    remove_segment,
    get_segment_count,
    get_segment_by_index
)

__all__ = [
    'add_media_segment',
    'add_text_segment', 
    'add_sticker_segment',
    'add_complex_text_segment',
    'add_filter_segment',
    'add_effect_segment',
    'add_audio_effect_segment',
    'add_internal_material_to_segment',
    'update_segment_transform',
    'update_text_material',
    'update_text_content',
    'update_adjust_info',
    'remove_segment',
    'get_segment_count',
    'get_segment_by_index'
]
