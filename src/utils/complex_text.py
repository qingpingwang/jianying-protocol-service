import uuid
from typing import Callable
from utils.models import *
from utils.function_utils import *

def get_material_by_id(material_id, materials_obj: dict) -> tuple[str, dict]:
    # 需要遍历每个key的value，如果value是list，则遍历每个元素，如果value是dict，则递归遍历
    for key, value in materials_obj.items():
        if not isinstance(value, list):
            continue
        for item in value:
            if item['id'] == material_id:
                return key, item
    return None, None

# 转换材质id，并添加素材到草稿
def convert_material_id_and_add_material(
    material_ids: list[str],
    materials_obj: dict, 
    add_material: Callable[[str, dict], str]
) -> list[str]:
    # material_ids去重
    material_ids = list(set(material_ids))
    new_material_ids = []
    for material_id in material_ids:
        # 查找materials_obj中id为material_id的素材
        material_type, material_obj = get_material_by_id(material_id, materials_obj)
        if not material_type or not material_obj:
            raise ValueError(f"素材{material_id}不存在")
        new_material_ids.append(add_material(material_type, material_obj))
    return new_material_ids

# 构建复杂文本片段，返回片段字典
def build_complex_text_segment(
    offset_time: int, 
    duration: int, 
    complex_text_material: JianYingTextComplexStyle, 
    add_material: Callable[[str, dict], str]
) -> dict:
    complex_text_material_dict = complex_text_material.complex_style_info
    # 将复杂文本素材转换为片段对象
    segment_obj = complex_text_material_dict['text_segment']
    materials_obj = complex_text_material_dict['materials']
    template_content_obj = complex_text_material_dict.get('template_content', None)
    
    # 1.转换额外引用材质ID
    extra_material_refs = segment_obj.get('extra_material_refs', [])
    new_extra_material_refs = convert_material_id_and_add_material(extra_material_refs, materials_obj, add_material)
    segment_obj['extra_material_refs'] = new_extra_material_refs
    
    # 文本样式适配
    text_material_id = segment_obj.get('material_id', None)
    text_material_type, text_material_obj = get_material_by_id(text_material_id, materials_obj)
    if not text_material_type or not text_material_obj:
        raise ValueError(f"复杂文本素材的文本材质{text_material_id}不存在")
    
    text_str = complex_text_material.text
    text_content = {
        'styles': [],
        'text': text_str
    }
    
    # 新增材质
    style_obj = json.loads(text_material_obj['content'])['styles'][0]
    style_obj['range'] = [0, len(text_str)]
    text_content['styles'].append(style_obj)
    text_material_obj['content'] = json.dumps(text_content)
    new_text_material_id = add_material(text_material_type, text_material_obj)
    segment_obj['material_id'] = new_text_material_id
    
    # 更新时间范围
    segment_obj['target_timerange']['start'] = offset_time
    segment_obj['target_timerange']['duration'] = duration
    
    # 生成新的片段ID
    segment_obj['id'] = str(uuid.uuid4())
    
    # 文字模板应用, todo
    return segment_obj
