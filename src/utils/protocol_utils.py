import os
import json
import uuid
import re
from dataclasses import dataclass
from typing import Optional
import logging
from urllib.parse import unquote, urlparse
from utils.complex_text import build_complex_text_segment
from utils.function_utils import *
from utils.oss_utils import OssMixin
from utils.models import *
import shutil


logger = logging.getLogger(__name__)


# ==================== 常量定义 ====================
# 剪映轨道类型: 音频轨道、视频轨道、特效轨道、滤镜轨道、文本轨道、贴纸轨道、调整轨道
JIANYING_TRACK_TYPES = ['audio', 'video', 'effect', 'filter', 'text', 'sticker', 'adjust']

# 剪映素材类型: 视频素材、文本素材、音频素材、贴纸素材、特效素材、视频特效素材、占位素材、转场素材、动画素材、倍速素材，滤镜在effects中
JIANYING_MATERIAL_TYPES = [
    'videos', 'texts', 'audios', 'stickers', 'effects', 'video_effects',
    'placeholders', 'transitions', 'material_animations', 'speeds'
]

# 片段类型配置：统一管理不同片段类型
SEGMENT_TYPE_CONFIG = {
    'sticker': {
        'material_type': 'stickers',
        'track_type': 'sticker',
        'required_material_type': 'sticker',
        'support_transform': True,
        'log_name': 'Sticker'
    },
    'filter': {
        'material_type': 'effects',
        'track_type': 'filter',
        'required_material_type': 'filter',
        'support_transform': False,
        'log_name': 'Filter'
    },
    'video_effect': {
        'material_type': 'video_effects',
        'track_type': 'effect',
        'required_material_type': 'video_effect',
        'support_transform': False,
        'log_name': 'Video Effect'
    }
}


# ==================== 协议处理器 ====================
class JianYingProtocol(OssMixin):
    """剪映协议处理器"""
    
    # ========== 初始化 ==========
    def __init__(self, jianying_data: JianYingData):
        super().__init__()
        self.data = jianying_data
        self._draft_info = jianying_data.draft_info
        self._draft_meta_info = jianying_data.draft_meta_info
        self._draft_virtual_store = jianying_data.draft_virtual_store
        self._base_info = jianying_data.baseInfo
    
    # ========== 属性 ==========
    @property
    def draft_info(self) -> dict:
        return self._draft_info
    
    @property
    def draft_meta_info(self) -> dict:
        return self._draft_meta_info
    
    @property
    def draft_virtual_store(self) -> dict:
        return self._draft_virtual_store
    
    @property
    def base_info(self) -> JianYingBaseInfo:
        return self._base_info
    
    @property
    def track_size(self) -> int:
        return len(self._draft_info['tracks'])
    
    # ========== 静态方法 ==========
    @staticmethod
    def parse_base_info_from_draft(draft_info: dict, draft_meta_info: dict) -> JianYingBaseInfo:
        """从草稿数据中解析基础信息"""
        canvas_info = draft_info['canvas_config']
        return JianYingBaseInfo(
            name=draft_meta_info['draft_name'],
            width=canvas_info['width'],
            height=canvas_info['height'],
            fps=draft_info['fps'],
            duration=draft_info['duration'] // 1000,
            unique_id=draft_info['id']
        )
    
    # ========== 项目管理 ==========
    def update_project_duration(self):
        """更新项目总时长"""
        max_duration = 0
        for i in range(self.track_size):
            track = self.get_track_by_index(i)
            if not track:
                continue
            duration = self.get_track_last_segment_time(track['id'])
            if duration > max_duration:
                max_duration = duration
        self.base_info.duration = max_duration // 1000
        self._draft_info['duration'] = int(max_duration)
    
    def get_relative_file_path(self, url: str) -> str:
        """获取资源相对路径"""
        file_name = url_to_filename(url)
        return f'./Resources/{file_name}'
    
    def get_absolute_file_path(self, url: str) -> str:
        """获取资源绝对路径"""
        return os.path.join(get_resource_path(self.data.baseInfo.unique_id), url_to_filename(url))
    
    def url_to_resource_path(self, url: str) -> str:
        """URL转资源路径（下载并返回草稿占位符路径）"""
        resource_path = get_resource_path(self.data.baseInfo.unique_id)
        file_name = url_to_filename(url)
        file_path = os.path.join(resource_path, file_name)
        if not os.path.exists(file_path):
            # 判断url是否以http开头，兼容本地文件和远程文件
            if url.startswith('http'):
                self.get_object_file(url, file_path)
            else:
                shutil.copy(os.getenv("JY_Res_Dir", "") + url, file_path)
        return f'##_draftpath_placeholder_0E685133-18CE-45ED-8CB8-2904A212EC80_##/Resources/{file_name}'
    
    # ==================== 轨道管理 ====================
    def add_track(self, track_type: str, index: int = -1) -> str:
        """添加轨道"""
        if track_type not in JIANYING_TRACK_TYPES:
            error_message = f"Invalid track type: {track_type}, just support {JIANYING_TRACK_TYPES}"
            logger.error(error_message)
            raise ValueError(error_message)
        
        new_track = build_track(track_type)
        
        if index == -1 or index >= self.track_size:
            self._draft_info['tracks'].append(new_track)
        else:
            self._draft_info['tracks'].insert(index, new_track)
        
        logger.info(f"Track added: type={track_type}, id={new_track['id']}, index={index}")
        return new_track['id']
    
    def remove_track(self, track_id: str) -> bool:
        """删除轨道"""
        tracks = self._draft_info['tracks']
        for i, track in enumerate(tracks):
            if track['id'] == track_id:
                del tracks[i]
                logger.info(f"Track removed: id={track_id}, index={i}")
                return True
        
        logger.warning(f"Track not found: {track_id}")
        return False
    
    def get_track_by_id(self, track_id: str) -> dict | None:
        """根据ID获取轨道"""
        tracks = self._draft_info['tracks']
        return next((track for track in tracks if track['id'] == track_id), None)
    
    def get_track_by_index(self, index: int) -> dict | None:
        """根据索引获取轨道"""
        tracks = self._draft_info['tracks']
        if index < 0 or index >= self.track_size:
            return None
        return tracks[index]
    
    def get_track_by_segment_id(self, segment_id: str) -> dict | None:
        """根据片段ID获取轨道"""
        return next(
            (track for track in self._draft_info['tracks'] 
             for seg in track['segments'] 
             if seg['id'] == segment_id), 
            None
        )
    
    def get_track_type_by_id(self, track_id: str) -> str | None:
        """获取轨道类型"""
        track = self.get_track_by_id(track_id)
        return track['type'] if 'type' in track else None
    
    def get_track_list(self) -> list[dict]:
        """获取所有轨道"""
        return self._draft_info['tracks']
    
    def get_track_last_segment_time(self, track_id: str) -> int:
        """获取轨道最后一个片段的结束时间（微秒）"""
        track = self.get_track_by_id(track_id)
        if not track:
            raise ValueError(f"Track not found: {track_id}")
        if len(track['segments']) == 0:
            return 0
        last_segment = track['segments'][-1]
        return last_segment['target_timerange']['start'] + last_segment['target_timerange']['duration']
    
    # ==================== 素材管理 ====================
    def get_materials_by_type(self, material_type: str) -> list[dict] | None:
        """获取指定类型的所有素材"""
        if material_type not in JIANYING_MATERIAL_TYPES:
            error_message = f"Invalid material type: {material_type}, just support {JIANYING_MATERIAL_TYPES}"
            logger.error(error_message)
            raise ValueError(error_message)
        return self._draft_info['materials'][material_type]
    
    def get_material(self, material_type: str, material_id: str) -> dict | None:
        """获取指定素材"""
        materials = self.get_materials_by_type(material_type)
        return next((m for m in materials if m['id'] == material_id), None)
    
    def get_material_by_index(self, material_type: str, index: int) -> dict | None:
        """根据索引获取素材"""
        materials = self.get_materials_by_type(material_type)
        if index < 0 or index >= self.get_materials_size(material_type):
            return None
        return materials[index]
    
    def get_materials_size(self, material_type: str) -> int:
        """获取素材数量"""
        return len(self.get_materials_by_type(material_type))
    
    def get_all_materials(self) -> dict:
        """获取所有素材"""
        return self._draft_info['materials']
    
    def add_material(self, material_type: str, material: dict) -> str:
        """添加素材"""
        materials = self.get_materials_by_type(material_type)
        material['id'] = str(uuid.uuid4())
        materials.append(material)
        return material['id']
    
    def update_material(self, material_type: str, material_id: str, material: dict) -> bool:
        """更新素材"""
        materials = self.get_materials_by_type(material_type)
        idx = next((i for i, m in enumerate(materials) if m['id'] == material_id), None)
        if idx is not None:
            material['id'] = material_id
            materials[idx] = material
            return True
        return False
    
    def remove_material(self, material_type: str, material_id: str) -> bool:
        """删除素材"""
        materials = self.get_materials_by_type(material_type)
        idx = next((i for i, m in enumerate(materials) if m['id'] == material_id), None)
        if idx is not None:
            del materials[idx]
            return True
        return False
    
    def remove_material_by_id(self, material_id: str) -> bool:
        """根据ID删除素材（自动识别类型）"""
        for material_type in JIANYING_MATERIAL_TYPES:
            materials = self.get_materials_by_type(material_type)
            idx = next((i for i, m in enumerate(materials) if m['id'] == material_id), None)
            if idx is None:
                continue
            # 删除素材
            remote_url = materials[idx].get('remote_url', None)
            del materials[idx]
            # 检查是否还有素材引用该文件
            if remote_url and not self.check_material_by_remote_url(remote_url):
                # 删除素材本地文件
                os.remove(self.get_absolute_file_path(remote_url))
                logger.info(f"Local material file deleted: {remote_url}")
                # 删除虚拟文件夹和素材元信息
                self.remove_meta_info_and_virtual_store_by_remote_url(remote_url)
            return True
        return False
    
    def check_material_by_remote_url(self, remote_url: str) -> bool:
        """检查是否还有素材引用该文件"""
        for material_type in JIANYING_MATERIAL_TYPES:
            materials = self.get_materials_by_type(material_type)
            for material in materials:
                if 'remote_url' not in material or material['remote_url'] != remote_url:
                    continue
                return True
        return False
    
    def add_material_to_draft_meta_info(self, material_meta_info: dict) -> str:
        """添加素材元信息"""
        draft_materials = self.draft_meta_info['draft_materials']
        material_meta_info['id'] = str(uuid.uuid4())
        draft_materials[0]['value'].append(material_meta_info)
        return material_meta_info['id']
    
    def add_material_to_virtual_store(self, media_material: JianYingMediaMaterialInfo, meta_id: str) -> bool:
        """添加展示素材到虚拟素材库"""
        draft_virtual_store_list1 = self.draft_virtual_store['draft_virtual_store'][1]['value']
        # meta_id 是否存在
        if next((item for item in draft_virtual_store_list1 if item['child_id'] == meta_id), None) is not None:
            return False
        # 查找分类是否存在
        category = media_material.category
        parent_id = ''
        # 如果分类不为空，则查找分类是否存在
        if category != '':
            draft_virtual_store_list0 = self.draft_virtual_store['draft_virtual_store'][0]['value']
            parent_id = next(
                (item['id'] for item in draft_virtual_store_list0 
                 if item['display_name'] == category), 
                None
            )
            # 如果分类不存在，则创建分类
            if not parent_id:
                parent_info = build_folder_info(category)
                parent_id = parent_info['id']
                draft_virtual_store_list0.append(parent_info)
                # 添加到根节点下
                draft_virtual_store_list1.append({
                    'child_id': parent_id,
                    'parent_id': ''
                })
                logger.info(f"Category created: {category}, id={parent_id}")
        # 添加素材到虚拟素材库
        draft_virtual_store_list1.append({
            'child_id': meta_id,
            'parent_id': parent_id
        })
        return True
    
    def remove_meta_info_and_virtual_store_by_remote_url(self, remote_url: str) -> bool:
        """移除虚拟文件夹和素材元信息（如果文件夹为空则同时删除文件夹）"""
        materials = self._draft_meta_info['draft_materials'][0]['value']
        virtual_folders = self.draft_virtual_store['draft_virtual_store'][0]['value']
        virtual_relations = self.draft_virtual_store['draft_virtual_store'][1]['value']
        
        # 1. 查找并删除素材元信息
        material = next((m for m in materials if m.get('remote_url') == remote_url), None)
        if not material:
            return False
        
        meta_id = material['id']
        materials.remove(material)
        
        # 2. 查找并删除虚拟关系
        relation = next((r for r in virtual_relations if r['child_id'] == meta_id), None)
        if not relation:
            return False
        
        parent_id = relation['parent_id']
        virtual_relations.remove(relation)
        
        # 3. 如果没有父文件夹或文件夹还有其他文件，则不删除文件夹
        if not parent_id:
            return True
        
        has_other_files = any(r['parent_id'] == parent_id for r in virtual_relations)
        if has_other_files:
            return True
        
        # 4. 删除空文件夹
        folder = next((f for f in virtual_folders if f['id'] == parent_id), None)
        if folder:
            virtual_folders.remove(folder)
        return True
    
    def is_material_meta_info_exists(self, media_material: JianYingMediaMaterialInfo) -> bool:
        """检查素材元信息是否已存在"""
        materials = self._draft_meta_info['draft_materials'][0]['value']
        return next(
            (m for m in materials if m['remote_url'] == media_material.url), 
            None
        ) is not None
    
    # ==================== 片段查询 ====================
    def get_track_segment_size(self, track_id: str) -> int:
        """获取轨道片段数量"""
        track = self.get_track_by_id(track_id)
        if not track:
            raise ValueError(f"Track not found: {track_id}")
        return len(track['segments'])
    
    def get_segment_by_index(self, track_id: str, index: int) -> dict | None:
        """根据索引获取片段"""
        track = self.get_track_by_id(track_id)
        if not track:
            raise ValueError(f"Track not found: {track_id}")
        if index < 0 or index >= len(track['segments']):
            return None
        return track['segments'][index]
    
    # ==================== 片段添加 ====================
    def add_media_segment_to_track(
        self, 
        track_id: str, 
        media_material: JianYingMediaMaterialInfo, 
        start_time: int | None = None, 
        transform_info: SegmentTransformInfo = None
    ) -> str:
        """添加媒体片段到轨道（视频、图片、音频）"""
        # 1. 验证轨道
        track = self.get_track_by_id(track_id)
        if not track:
            raise ValueError(f"Track not found: {track_id}")
        self.check_media_track_type(track['type'], media_material)
        
        # 2. 计算时长和时间
        duration = self._calculate_media_duration(media_material)
        
        # 3. 创建材质
        is_footage = media_material.media_type in ['video', 'photo']
        material_id = self._create_media_material(media_material, is_footage)
        speed_id = self.add_material('speeds', build_speed(media_material.speed))
        
        # 4. 构建片段
        segment = build_media_segment(
            material_id=material_id,
            offset_time=self._calculate_offset_time(track_id, start_time),
            from_time=int(media_material.from_time * 1000),
            duration=duration,
            speed=media_material.speed,
            volume=0.0 if media_material.mute else 1.0
        )
        
        # 5. 添加额外信息
        if is_footage:
            if transform_info:
                segment = self.add_transform_info_to_segment(segment, transform_info)
            if media_material.adjust_info:
                self.add_adjust_info_to_segment(segment, media_material.adjust_info)
        
        segment['extra_material_refs'].append(speed_id)
        
        # 6. 完成片段添加
        segment_id = self._finalize_segment(track, segment)
        
        # 7. 添加素材元信息
        self._add_media_meta_info_if_needed(media_material)
        
        logger.info(
            f"Media segment added: type={media_material.media_type}, "
            f"material={material_id}, segment={segment_id}, "
            f"project_duration={self.base_info.duration}"
        )
        return segment_id
    
    def add_audio_effect_segment_to_track(
        self, 
        track_id: str, 
        audio_material: dict, 
        start_time: int | None = None
    ) -> str:
        """添加音效片段到轨道"""
        # 1. 验证
        track = self._validate_and_get_track(track_id, 'audio')
        if not track:
            raise ValueError(f"Track not found: {track_id}")
        # 创建材质
        material_id = self.add_material('audios', audio_material)
        # 构建片段
        segment = build_media_segment(
            material_id=material_id,
            offset_time=self._calculate_offset_time(track_id, start_time),
            from_time=0,
            duration=audio_material['duration'],
            speed=1.0,
            volume=1.0
        )
        # 完成片段
        segment_id = self._finalize_segment(track, segment)
        return segment_id
    
    def add_text_segment_to_track(
        self, 
        track_id: str, 
        text_material: JianYingTextMaterialInfo, 
        start_time: int | None = None, 
        duration: int = 5000,
        transform_info: SegmentTransformInfo = None
    ) -> str:
        """添加文本片段到文本轨道"""
        # 1. 验证
        track = self._validate_and_get_track(track_id, 'text')
        self._validate_duration(duration)
        
        # 2. 创建材质
        material_id = self.add_material(
            'texts',
            build_text_material(
                text=text_material.text,
                content=text_material.model_dump_json(),
                background_color=text_material.background_color,
                background_alpha=text_material.background_alpha
            )
        )
        
        # 3. 构建片段
        segment = build_segmen_no_source(
            material_id=material_id,
            offset_time=self._calculate_offset_time(track_id, start_time),
            duration=duration * 1000
        )
        if transform_info:
            segment = self.add_transform_info_to_segment(segment, transform_info)
        
        # 4. 完成
        segment_id = self._finalize_segment(track, segment)
        
        logger.info(
            f"Text segment added: text={text_material.text}, "
            f"material={material_id}, segment={segment_id}, "
            f"duration={duration}ms, project_duration={self.base_info.duration}"
        )
        return segment_id
    
    def add_complex_text_segment_to_track(
        self, 
        track_id: str, 
        complex_text_material: JianYingTextComplexStyle, 
        start_time: int | None = None, 
        duration: int = 5000, 
        transform_info: SegmentTransformInfo = None
    ) -> str:
        """添加复杂文本片段到文本轨道"""
        # 1. 验证
        track = self._validate_and_get_track(track_id, 'text')
        self._validate_duration(duration)
        
        # 2. 构建片段（复杂文本通过辅助函数构建，内部生成ID和材质）
        segment = build_complex_text_segment(
            self._calculate_offset_time(track_id, start_time),
            duration * 1000, 
            complex_text_material, 
            self.add_material
        )
        if transform_info:
            segment = self.add_transform_info_to_segment(segment, transform_info)
        
        # 3. 完成（复杂文本的ID已在 build_complex_text_segment 中生成）
        segment_id = segment['id']
        track['segments'].append(segment)
        self.update_project_duration()
        
        logger.info(
            f"Complex text segment added: text={complex_text_material.text}, "
            f"segment={segment_id}, "
            f"duration={duration}ms, project_duration={self.base_info.duration}"
        )
        return segment_id
    
    def add_sticker_segment_to_track(
        self, 
        track_id: str, 
        sticker_material: JianYingInternalMaterialInfo, 
        start_time: int | None = None, 
        duration: int = 5000, 
        transform_info: SegmentTransformInfo = None
    ) -> str:
        """添加贴纸片段到贴纸轨道"""
        return self._add_simple_segment_to_track(
            track_id, 'sticker', sticker_material, 
            start_time, duration, transform_info
        )
    
    def add_filter_segment_to_track(
        self, 
        track_id: str, 
        filter_material: JianYingInternalMaterialInfo, 
        start_time: int | None = None, 
        duration: int = 5000
    ) -> str:
        """添加滤镜片段到滤镜轨道"""
        return self._add_simple_segment_to_track(
            track_id, 'filter', filter_material, 
            start_time, duration
        )
    
    def add_effect_segment_to_track(
        self, 
        track_id: str, 
        effect_material: JianYingInternalMaterialInfo, 
        start_time: int | None = None, 
        duration: int = 5000
    ) -> str:
        """添加视频特效片段到特效轨道"""
        return self._add_simple_segment_to_track(
            track_id, 'video_effect', effect_material, 
            start_time, duration
        )
    
    def add_internal_material_to_segment(
        self, 
        segment_id: str, 
        internal_material: JianYingInternalMaterialInfo
    ) -> str:
        """添加内部材质到片段（动画、转场、特效、滤镜）"""
        # 类型映射配置
        type_mapping = {
            'sticker_animation': 'material_animations',
            'transition': 'transitions',
            "video_effect": "video_effects",
            "filter": "effects"
        }
        
        track = self.get_track_by_segment_id(segment_id)
        if not track:
            raise ValueError(f"Track not found for segment: {segment_id}")
        
        segment = next((seg for seg in track['segments'] if seg['id'] == segment_id), None)
        if not segment:
            raise ValueError(f"Segment not found: {segment_id}")
        
        material_info = internal_material.material_info
        material_type = type_mapping.get(material_info.get('type'), None)
        if not material_type:
            raise ValueError(f"Material type not supported: {material_info.get('type')}")
        
        material_id = self.add_material(material_type, material_info)
        segment['extra_material_refs'].append(material_id)
        return material_id
    
    # ==================== 片段更新 ====================
    def update_text_material_info(
        self, 
        segment_id: str, 
        text_material: JianYingTextMaterialInfo
    ) -> str:
        """更新文本素材信息"""
        track = self.get_track_by_segment_id(segment_id)
        if not track:
            raise ValueError(f"Track not found: {segment_id}")
        if track['type'] != 'text':
            raise ValueError(f"Track type not supported: {track['type']}, expected: text")
        
        segment = next((seg for seg in track['segments'] if seg['id'] == segment_id), None)
        if not segment:
            raise ValueError(f"Segment not found: {segment_id}")
        
        ret = self.update_material('texts', segment['material_id'], build_text_material(
            text=text_material.text,
            content=text_material.model_dump_json(),
            background_color=text_material.background_color,
            background_alpha=text_material.background_alpha
        ))
        if not ret:
            raise ValueError(f"Failed to update text material: {segment_id}")
        return segment['id']
    
    def update_text_content(
        self, 
        segment_id: str, 
        text: str
    ) -> str:
        """更新文本内容"""
        track = self.get_track_by_segment_id(segment_id)
        if not track:
            raise ValueError(f"Track not found: {segment_id}")
    
        segment = next((seg for seg in track['segments'] if seg['id'] == segment_id), None)
        if not segment:
            raise ValueError(f"Segment not found: {segment_id}")
        
        material = self.get_material('texts', segment['material_id'])
        if not material:
            raise ValueError(f"Material not found: {segment['material_id']}")
        material['text'] = text
        content = json.loads(material['content'])
        content['text'] = text
        content['styles'][0]['range'] = [0, len(text)]
        material['content'] = json.dumps(content)
        self.update_material('texts', segment['material_id'], material)
        return segment['id']
    
    def update_segment_transform_info(
        self, 
        segment_id: str, 
        transform_info: SegmentTransformInfo
    ) -> str:
        """更新片段变换信息"""
        track = self.get_track_by_segment_id(segment_id)
        if not track:
            raise ValueError(f"Track not found: {segment_id}")
        if track['type'] not in ['video', 'text', 'sticker']:
            raise ValueError(f"Track type not supported: {track['type']}, expected: video, text, sticker")
        
        segment = next((seg for seg in track['segments'] if seg['id'] == segment_id), None)
        if not segment:
            raise ValueError(f"Segment not found: {segment_id}")
        
        self.add_transform_info_to_segment(segment, transform_info)
        return segment['id']
    
    def update_segment_adjust_info(
        self, 
        segment_id: str, 
        adjust_info: AdjustInfo
    ) -> str:
        """更新片段调色信息"""
        track = self.get_track_by_segment_id(segment_id)
        if not track:
            raise ValueError(f"Track not found: {segment_id}")
        if track['type'] != 'video':
            raise ValueError(f"Track type not supported: {track['type']}, expected: video")
        
        segment = next((seg for seg in track['segments'] if seg['id'] == segment_id), None)
        if not segment:
            raise ValueError(f"Segment not found: {segment_id}")
        
        # 需要移除原有调色信息
        new_extra_material_refs = []
        for extra_material_id in segment['extra_material_refs']:
            # 获取素材
            effect_material = self.get_material('effects', extra_material_id)
            # 保留非调色类型的素材
            if not effect_material or effect_material.get('type') not in AdjustInfo.model_fields.keys():
                new_extra_material_refs.append(extra_material_id)
                continue
            # 移除旧的调色素材
            self.remove_material('effects', extra_material_id)
        
        # 更新片段的素材引用列表
        segment['extra_material_refs'] = new_extra_material_refs
        
        # 添加新的调色信息
        self.add_adjust_info_to_segment(segment, adjust_info)
        
        return segment['id']
    
    # ==================== 片段删除 ====================
    def remove_segment_by_id(self, segment_id: str) -> bool:
        """删除片段"""
        track = self.get_track_by_segment_id(segment_id)
        if not track:
            return False
        
        segment = next((seg for seg in track['segments'] if seg['id'] == segment_id), None)
        if not segment:
            return False
        
        self._remove_segment_materials(segment)
        track['segments'].remove(segment)
        self.update_project_duration()
        logger.info(f"Segment removed: segment={segment_id}, project_duration={self.base_info.duration}")
        return True
    
    # ==================== 辅助方法（公开） ====================
    def check_media_track_type(self, track_type: str, media_material: JianYingMediaMaterialInfo) -> bool:
        """验证媒体素材和轨道类型是否匹配"""
        type_map = {
            ('video', 'photo'): 'video',
            ('audio', 'oral'): 'audio'
        }
        
        for media_types, expected_track in type_map.items():
            if media_material.media_type in media_types and track_type != expected_track:
                error_msg = (
                    f"Material type '{media_material.media_type}' requires "
                    f"'{expected_track}' track, got '{track_type}'"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
        return True
    
    def add_transform_info_to_segment(self, segment: dict, transform_info: SegmentTransformInfo):
        """添加变换信息到片段"""
        if transform_info is None:
            return segment
            
        segment['clip'] = {
            "alpha": 1.0,
            "flip": {
                "horizontal": False,
                "vertical": False
            },
            "rotation": float(transform_info.rotate),
            "scale": {
                "x": float(transform_info.scale_x),
                "y": float(transform_info.scale_y)
            },
            "transform": {
                "x": float(transform_info.translate_x),
                "y": float(transform_info.translate_y)
            }
        }
        return segment
    
    def add_adjust_info_to_segment(self, segment: dict, adjust_info: AdjustInfo):
        """添加调色信息到片段"""
        for field_name, value in adjust_info.model_dump().items():
            # 忽略默认值 0
            if value == 0:
                continue
                
            # 获取元数据
            field = AdjustInfo.model_fields[field_name]
           
            ge = None
            le = None
            # Pydantic v2: 约束在 metadata 列表中
            for metadata in field.metadata:
                if hasattr(metadata, 'ge'): 
                    ge = metadata.ge
                if hasattr(metadata, 'le'): 
                    le = metadata.le    
            
            if ge is None or le is None:
                continue
            
            # 正则提取版本号
            description = field.description
            match = re.search(r'(v\d+)', description)
            version = match.group(1) if match else ""
                
            # 归一化获取 value
            normalized_value = normalize_adjust_value(value, ge, le)
            
            adjust_material = build_adjust_material(normalized_value, field_name, version)
            adjust_material_id = self.add_material('effects', adjust_material)
            # 添加进额外材质引用
            segment['extra_material_refs'].append(adjust_material_id)
        return  
    
    # ==================== 内部方法（私有） ====================
    # 验证方法
    def _validate_material_type(self, material: JianYingInternalMaterialInfo, expected_type: str) -> None:
        """验证材质类型"""
        actual_type = material.material_info.get('type')
        if actual_type != expected_type:
            raise ValueError(
                f"Material type not supported: {actual_type}, expected: {expected_type}"
            )
    
    def _validate_and_get_track(self, track_id: str, expected_type: str) -> dict:
        """验证并获取轨道"""
        track = self.get_track_by_id(track_id)
        if not track:
            raise ValueError(f"Track not found: {track_id}")
        if track['type'] != expected_type:
            raise ValueError(
                f"Track type not supported: {track['type']}, expected: {expected_type}"
            )
        return track
    
    def _validate_duration(self, duration: int) -> None:
        """验证时长"""
        if duration <= 0:
            raise ValueError(f"Duration must be greater than 0, got: {duration}")
    
    # 计算方法
    def _calculate_offset_time(self, track_id: str, start_time: int | None) -> int:
        """计算片段开始时间（微秒）"""
        return int(start_time * 1000) if start_time is not None else self.get_track_last_segment_time(track_id)
    
    def _calculate_media_duration(self, media_material: JianYingMediaMaterialInfo) -> int:
        """计算媒体素材时长（微秒）"""
        duration = int(media_material.to_time - media_material.from_time) * 1000
        if duration <= 0:
            duration = media_material.duration * 1000
        if duration <= 0:
            raise ValueError(f"Duration is less than 0: {duration}, media_material: {media_material}")
        # 考虑倍速
        return int(duration / media_material.speed)
    
    # 创建和生成方法
    def _generate_segment_id(self, segment: dict) -> str:
        """生成并设置片段ID"""
        segment_id = str(uuid.uuid4())
        segment['id'] = segment_id
        return segment_id
    
    def _create_media_material(self, media_material: JianYingMediaMaterialInfo, is_footage: bool) -> str:
        """创建媒体材质并返回材质ID"""
        if is_footage:
            material = build_video_or_photo_material(
                url=media_material.url,
                path=self.url_to_resource_path(media_material.url),
                width=media_material.width,
                height=media_material.height,
                name=media_material.material_name
            )
            # 添加裁剪信息
            if media_material.clip_info:
                clip_info = media_material.clip_info
                material['crop'] = build_crop_info(
                    top_x=clip_info.left_top_x,
                    top_y=clip_info.left_top_y,
                    width=clip_info.width,
                    height=clip_info.height
                )
                material['crop_ratio'] = 'free'
            return self.add_material('videos', material)
        elif media_material.media_type in ['audio', 'oral']:
            material = build_audio_material(
                url=media_material.url,
                path=self.url_to_resource_path(media_material.url),
                name=media_material.material_name,
                is_sound=(media_material.media_type == 'oral')
            )
            return self.add_material('audios', material)
        else:
            raise ValueError(
                f"Material type not supported: {media_material.media_type}, "
                f"just support video, photo, audio, oral"
            )
    
    # 完成和清理方法
    def _finalize_segment(self, track: dict, segment: dict) -> str:
        """完成片段添加：生成ID、添加到轨道、更新时长"""
        segment_id = self._generate_segment_id(segment)
        track['segments'].append(segment)
        self.update_project_duration()
        return segment_id
    
    def _remove_segment_materials(self, segment: dict) -> None:
        """移除片段的所有材质"""
        self.remove_material_by_id(segment['material_id'])
        for material_id in segment['extra_material_refs']:
            self.remove_material_by_id(material_id)
    
    def _add_media_meta_info_if_needed(self, media_material: JianYingMediaMaterialInfo) -> None:
        """添加媒体素材元信息到虚拟素材库（如果尚未存在）"""
        if self.is_material_meta_info_exists(media_material):
            return
        
        # 确定素材类型
        if media_material.media_type in ['audio', 'oral']:
            meta_type = 'music'
        else:
            meta_type = get_material_type_by_extension(media_material.url)
        
        # 构建元信息
        material_meta_info = build_material_meta_info(
            extra_info=media_material.material_name,
            file_path=self.get_relative_file_path(media_material.url),
            remote_url=media_material.url,
            duration=media_material.duration,
            material_type=meta_type,
            width=media_material.width,
            height=media_material.height
        )
        material_meta_id = self.add_material_to_draft_meta_info(material_meta_info)
        self.add_material_to_virtual_store(media_material, material_meta_id)
    
    # 通用片段操作
    def _add_simple_segment_to_track(
        self,
        track_id: str,
        segment_type: str,
        material: JianYingInternalMaterialInfo,
        start_time: int | None = None,
        duration: int = 5000,
        transform_info: Optional[SegmentTransformInfo] = None
    ) -> str:
        """通用的简单片段添加方法"""
        # 1. 获取配置
        config = SEGMENT_TYPE_CONFIG.get(segment_type)
        if not config:
            raise ValueError(f"Unknown segment type: {segment_type}")
        
        # 2. 验证
        if config['required_material_type']:
            self._validate_material_type(material, config['required_material_type'])
        track = self._validate_and_get_track(track_id, config['track_type'])
        
        # 3. 添加材质
        material_id = self.add_material(config['material_type'], material.material_info)
        
        # 4. 构建片段
        segment = build_segmen_no_source(
            material_id=material_id,
            offset_time=self._calculate_offset_time(track_id, start_time),
            duration=duration * 1000
        )
        segment["material_id"] = material_id
        
        # 5. 添加transform（如果支持）
        if config['support_transform'] and transform_info:
            segment = self.add_transform_info_to_segment(segment, transform_info)
        
        # 6. 完成
        segment_id = self._finalize_segment(track, segment)
        
        logger.info(
            f"{config['log_name']} segment added: material={material_id}, "
            f"segment={segment_id}, project_duration={self.base_info.duration}"
        )
        return segment_id
