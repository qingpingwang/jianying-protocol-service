import os
import json
import uuid
import zipfile
import threading
import logging
from datetime import datetime
import urllib.parse
from utils.models import JianYingBaseInfo, JianYingData
from utils.protocol_utils import JianYingProtocol
from utils.function_utils import *
logger = logging.getLogger(__name__)



class JianYingProject():
    """
    剪映工程管理器（纯工程生命周期管理）
    
    设计原则：
    - **单一职责**：只管工程的创建、加载、保存、导出
    - **数据隔离**：所有数据操作通过 `self.protocol` 完成
    - **简洁接口**：对外只暴露工程级函数，不暴露数据访问方法
    
    使用示例：
        # 创建工程
        project = JianYingProject(baseInfo)
        
        # 操作数据（通过 protocol）
        project.protocol.add_track('video')
        project.protocol.add_material('videos', {...})
        
        # 保存工程
        project.save()
        
        # 导出到 OSS
        url = project.export_to_oss()
    """
    
    def __init__(self, baseInfo: JianYingBaseInfo):
        super().__init__()  # 初始化 OssMixin
        
        # 如果 unique_id 为空，创建新对象（避免修改传入参数）
        if baseInfo.unique_id is None:
            baseInfo = JianYingBaseInfo(
                name=baseInfo.name,
                width=baseInfo.width,
                height=baseInfo.height,
                fps=baseInfo.fps,
                duration=baseInfo.duration,
                unique_id=str(uuid.uuid4())
            )
        
        # 加载或构建数据，并初始化协议处理器
        jianying_data = self._get_jianying_data(baseInfo)
        
        # 协议处理器：数据的唯一来源（公开访问）
        self.protocol = JianYingProtocol(jianying_data)
        self.project_remote_path = os.getenv('PROJECT_REMOTE_PATH', None)
        assert self.project_remote_path, 'PROJECT_REMOTE_PATH is not set'
        
    # ==================== 公共接口（工程级操作）====================
    
    def save(self):
        """
        保存工程到磁盘（原子写入）
        
        使用场景：
        - 修改数据后手动保存
        - 在 taskManager 中由 acquire() 自动调用
        """
        self._update_data_to_disk()
    
    def export_to_oss(self) -> str:
        """
        导出工程到 OSS（异步执行）
        
        Returns:
            OSS URL（立即返回，后台异步压缩上传）
        """
        return self._compress_and_upload_to_oss()
    
    def get_project_absolute_path(self):
        """
        返回项目绝对路径
        """
        return get_project_path(self.protocol.base_info.unique_id)
    
    # ==================== 内部方法 ====================
    
    def _get_jianying_data(self, baseInfo: JianYingBaseInfo) -> JianYingData:
        """加载或构建数据（内部使用）"""
        if self._can_use_cache(baseInfo):
            return self._load_cache_data(baseInfo.unique_id)
        else:
            return self._build_jianying_data(baseInfo)
    
    def _can_use_cache(self, baseInfo: JianYingBaseInfo) -> bool:
        """检查缓存是否可用"""
        filePath = get_project_path(baseInfo.unique_id)
        path_list = [filePath, get_draft_path(filePath), get_draft_meta_info_path(filePath)]
        return all(os.path.exists(path) for path in path_list)
    
  
    def _load_cache_data(self, unique_id: str) -> JianYingData:
        """从磁盘加载数据"""
        project_path = get_project_path(unique_id)
        
        # 加载 JSON 文件
        draft_info = load_json_data(get_draft_path(project_path))
        draft_meta_info = load_json_data(get_draft_meta_info_path(project_path))
        draft_virtual_store = load_json_data(get_draft_virtual_store_path(project_path))
        
        # 使用协议处理器解析 BaseInfo
        baseInfo = JianYingProtocol.parse_base_info_from_draft(draft_info, draft_meta_info)
        
        logger.info(f"从缓存加载工程: {unique_id}")
        return JianYingData(baseInfo, draft_info, draft_meta_info, draft_virtual_store)
    
    def _flush(self):
        """刷新数据到内存"""
        jianying_data = self._get_jianying_data(self.protocol.base_info)
        self.protocol = JianYingProtocol(jianying_data)

    def _update_data_to_disk(self):
        """更新数据到磁盘（原子写入）"""
        project_path = get_project_path(self.protocol.base_info.unique_id)
        
        # 落盘
        write_json_file(self.protocol.draft_info, get_draft_path(project_path))
        write_json_file(self.protocol.draft_meta_info, get_draft_meta_info_path(project_path))
        write_json_file(self.protocol.draft_virtual_store, get_draft_virtual_store_path(project_path))
    
    def _build_jianying_data(self, baseInfo: JianYingBaseInfo) -> JianYingData:
        """构建新工程（内部使用）"""
        project_path = get_project_path(baseInfo.unique_id)
        resource_path = get_resource_path(baseInfo.unique_id)
        
        # 创建目录结构
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            os.makedirs(resource_path)
        
        # 构建数据结构
        draft_info = build_draft_info(
            baseInfo.unique_id, 
            baseInfo.width, 
            baseInfo.height, 
            baseInfo.duration, 
            baseInfo.fps
        )
        draft_meta_info = build_draft_meta_info(baseInfo.name)
        draft_virtual_store = build_draft_virtual_store()
        # 创建数据对象
        jianying_data = JianYingData(baseInfo, draft_info, draft_meta_info, draft_virtual_store)
        logger.info(f"创建新工程: {baseInfo.unique_id}")
        # 落盘
        write_json_file(draft_info, get_draft_path(project_path)) 
        write_json_file(draft_meta_info, get_draft_meta_info_path(project_path))
        write_json_file(draft_virtual_store, get_draft_virtual_store_path(project_path))
        return jianying_data
    
    def _do_compress_and_upload(self, remote_url: str, zip_file_path: str):
        """
        实际执行压缩和上传（内部方法，由后台线程调用）
        
        Args:
            remote_url: OSS 目标 URL
            zip_file_path: 本地压缩包路径
        """
        try:
            # 1. 压缩文件
            project_path = get_project_path(self.protocol.base_info.unique_id)
            logger.info(f"开始压缩文件: {project_path}")
            
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_path):
                    for file in files:
                        # 跳过临时文件
                        if file.startswith('.tmp_'):
                            continue
                        
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_path)
                        
                        # 再次检查文件是否存在（防止竞态条件）
                        if os.path.exists(file_path):
                            zipf.write(file_path, arcname)
            
            logger.info(f"压缩完成，开始上传: {remote_url}")
            
            # 2. 上传到 OSS（继承自 OssMixin）
            self.protocol.post_object_file(remote_url, zip_file_path)
            
            logger.info(f"上传成功: {remote_url}")
            
            # 3. 删除本地临时压缩包
            if os.path.exists(zip_file_path):
                os.remove(zip_file_path)
                logger.info(f"已删除本地压缩包: {zip_file_path}")
                
        except Exception as e:
            logger.error(f"压缩上传失败: {remote_url}, 错误: {e}", exc_info=True)
            # 清理失败的临时文件
            if os.path.exists(zip_file_path):
                try:
                    os.remove(zip_file_path)
                except:
                    pass
    
    def _compress_and_upload_to_oss(self) -> str:
        """
        压缩并上传到 OSS（异步执行）
        
        立即返回预生成的 OSS URL，后台线程执行压缩和上传。
        注意：返回的 URL 立即可用，但文件需要等待压缩上传完成后才能访问。
        
        Returns:
            OSS URL（预生成）
        """
        # 1. 生成 OSS URL（提前返回）
        time = datetime.now()
        unique_id = self.protocol.base_info.unique_id
        # 远端名称使用项目名称，URL 编码
        remote_name = urllib.parse.quote(self.protocol.base_info.name)
        date_str = time.strftime("%Y%m%d")
        timestamp_str = time.strftime("%Y%m%d%H%M%S%f")
        remote_url = f'{self.project_remote_path}/{date_str}/{timestamp_str}/{remote_name}.zip'
        
        # 2. 落盘操作（确保数据最新）
        self._update_data_to_disk()
        
        # 3. 本地临时压缩包路径
        project_path = get_project_path(unique_id)
        zip_file_path = f'{project_path}.zip'
        
        # 4. 启动后台线程执行压缩上传
        thread = threading.Thread(
            target=self._do_compress_and_upload,
            args=(remote_url, zip_file_path),
            daemon=True,  # 守护线程，主进程退出时自动结束
            name=f"compress-upload-{unique_id[:8]}"
        )
        thread.start()
        
        logger.info(f"已创建异步压缩上传任务: {remote_url}")
        
        # 5. 立即返回 URL
        return remote_url

