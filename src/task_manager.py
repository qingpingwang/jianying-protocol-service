from jianying_project import JianYingProject
from utils.models import JianYingBaseInfo
from utils.function_utils import *
import threading
import time
import logging
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# 超过60s闲置,则移出内存
TASK_IDLE_TIME = 60


class JianYingTask:
    """剪映任务封装 - 线程安全"""
    
    def __init__(self, baseInfo: JianYingBaseInfo):
        self.jianyingProject = JianYingProject(baseInfo)
        self.lock = threading.RLock()  # 任务锁
        self.last_access_time = time.time()
    
    @contextmanager
    def acquire(self):
        """
        获取任务锁的上下文管理器
        
        自动落盘：退出时自动保存数据到磁盘
        
        Usage:
            with task.acquire():
                # 操作任务，退出时自动落盘
                task.jianyingProject.do_something()
        """
        with self.lock:
            self.last_access_time = time.time()  # 进入时更新
            try:
                yield self
                # 只有业务逻辑执行成功（无异常）才落盘
                try:
                    self.jianyingProject.save()
                except Exception as e:
                    logger.error(f"任务落盘失败: {e}", exc_info=True)
                    self.jianyingProject._flush()
            except Exception:
                # 发生异常时刷新数据到内存，避免脏数据影响后续操作
                self.jianyingProject._flush()
                raise
            finally:
                self.last_access_time = time.time()  # 退出时更新
    
    def is_expired(self, expire_seconds: int) -> bool:
        """检查任务是否过期且未使用（线程安全）"""
        # 尝试获取锁，如果锁被持有说明正在使用
        acquired = self.lock.acquire(blocking=False)
        if not acquired:
            return False  # 锁被持有，任务正在使用
        
        try:
            # 检查最后访问时间
            elapsed = time.time() - self.last_access_time
            return elapsed > expire_seconds
        finally:
            self.lock.release()


class TaskManager:
    """任务管理器 - 简化版"""
    
    def __init__(self):
        # 字典：task_id -> JianYingTask
        self.task_dict = {}
        # 全局锁：保护 task_dict 和所有任务操作
        self.lock = threading.RLock()
        # 启动后台清理线程
        cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_loop(self):
        """后台清理线程"""
        while True:
            time.sleep(5)
            self._remove_expired_tasks()
    
    def _remove_expired_tasks(self):
        """移除过期任务"""
        with self.lock:
            expired_ids = [
                task_id for task_id, task in self.task_dict.items()
                if task.is_expired(TASK_IDLE_TIME)
            ]
            
            for task_id in expired_ids:
                del self.task_dict[task_id]
                logger.info(f"清理闲置任务: {task_id}")
    
    def create_task(self, baseInfo: JianYingBaseInfo) -> str:
        """
        创建新任务
        
        返回：task_id (unique_id)
        """
        with self.lock:
            # 创建任务（在锁内，保证原子性）
            task = JianYingTask(baseInfo)
            task_id = task.jianyingProject.protocol.base_info.unique_id
            
            # 检查是否已存在
            if task_id in self.task_dict:
                logger.warning(f"任务已存在: {task_id}")
                return task_id
            
            self.task_dict[task_id] = task
            logger.info(f"创建任务: {task_id}")
            return task_id
    
    def _load_task_from_disk(self, task_id: str) -> JianYingTask | None:
        """从磁盘加载任务（内部方法，调用时必须在锁外）"""
        project_path = get_project_path(task_id)
        if not os.path.exists(project_path):
            return None
        
        try:
            baseInfo = JianYingBaseInfo.from_unique_id(task_id)
            return JianYingTask(baseInfo)
        except Exception as e:
            logger.error(f"从磁盘加载任务失败: {task_id}, {e}")
            return None
    
    @contextmanager
    def get_task(self, task_id: str):
        """
        获取任务（上下文管理器）
        
        Usage:
            with taskManager.get_task(task_id) as task:
                if task:
                    # 操作任务（自动加锁，多线程安全）
                    task.jianyingProject.save()
        
        说明：
        1. 自动加锁，多线程访问同一任务会排队
        2. 自动更新访问时间，防止被清理
        3. 如果内存中没有，自动从磁盘加载
        """
        # 步骤1：从内存获取任务（快速路径）
        task = None
        with self.lock:
            if task_id in self.task_dict:
                task = self.task_dict[task_id]
        
        # 如果找到任务，在锁外获取任务锁（避免嵌套锁）
        if task:
            with task.acquire():
                yield task
            return
        
        # 步骤2：从磁盘加载（慢速路径，在锁外执行）
        task = self._load_task_from_disk(task_id)
        
        if not task:
            yield None
            return
        
        # 步骤3：插入字典
        with self.lock:
            # 双重检查：可能其他线程已加载
            if task_id in self.task_dict:
                task = self.task_dict[task_id]
            else:
                self.task_dict[task_id] = task
                logger.info(f"从磁盘加载任务: {task_id}")
        
        # 步骤4：获取任务锁并使用
        with task.acquire():
            yield task

