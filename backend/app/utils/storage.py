"""
文件存储工具
支持本地存储和阿里云 OSS
"""
import os
import uuid
from datetime import datetime
from typing import Optional

from app.config import settings


def generate_filename(original_filename: str) -> str:
    """
    生成唯一文件名
    
    Args:
        original_filename: 原始文件名
    
    Returns:
        唯一文件名
    """
    ext = original_filename.rsplit('.', 1)[-1] if '.' in original_filename else ''
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique_id}.{ext}"


def get_storage_path() -> str:
    """
    获取存储路径
    
    Returns:
        存储路径
    """
    if settings.STORAGE_TYPE == "local":
        return settings.LOCAL_STORAGE_PATH
    return ""


def ensure_directory(path: str) -> None:
    """
    确保目录存在
    
    Args:
        path: 目录路径
    """
    os.makedirs(path, exist_ok=True)


async def save_file(file_data: bytes, filename: str, folder: str = "") -> str:
    """
    保存文件
    
    Args:
        file_data: 文件数据
        filename: 文件名
        folder: 子文件夹
    
    Returns:
        文件访问 URL
    """
    if settings.STORAGE_TYPE == "local":
        return await _save_local(file_data, filename, folder)
    elif settings.STORAGE_TYPE == "oss":
        return await _save_oss(file_data, filename, folder)
    else:
        raise ValueError(f"不支持的存储类型: {settings.STORAGE_TYPE}")


async def _save_local(file_data: bytes, filename: str, folder: str = "") -> str:
    """
    保存到本地
    
    Args:
        file_data: 文件数据
        filename: 文件名
        folder: 子文件夹
    
    Returns:
        文件访问 URL
    """
    # 生成唯一文件名
    unique_filename = generate_filename(filename)
    
    # 构建存储路径
    storage_path = get_storage_path()
    if folder:
        storage_path = os.path.join(storage_path, folder)
    
    # 按日期组织文件
    today = datetime.now().strftime("%Y/%m/%d")
    storage_path = os.path.join(storage_path, today)
    
    # 确保目录存在
    ensure_directory(storage_path)
    
    # 保存文件
    file_path = os.path.join(storage_path, unique_filename)
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    # 返回访问 URL
    return f"/uploads/{folder}/{today}/{unique_filename}" if folder else f"/uploads/{today}/{unique_filename}"


async def _save_oss(file_data: bytes, filename: str, folder: str = "") -> str:
    """
    保存到阿里云 OSS
    
    Args:
        file_data: 文件数据
        filename: 文件名
        folder: 子文件夹
    
    Returns:
        文件访问 URL
    """
    # TODO: 实现 OSS 上传
    # import oss2
    # auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
    # bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET)
    # 
    # unique_filename = generate_filename(filename)
    # if folder:
    #     unique_filename = f"{folder}/{unique_filename}"
    # 
    # bucket.put_object(unique_filename, file_data)
    # return f"https://{settings.OSS_BUCKET}.{settings.OSS_ENDPOINT}/{unique_filename}"
    
    raise NotImplementedError("OSS 存储暂未实现")


def get_file_url(file_path: str) -> str:
    """
    获取文件访问 URL
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件访问 URL
    """
    if file_path.startswith("http"):
        return file_path
    
    if settings.STORAGE_TYPE == "local":
        return file_path
    
    # OSS 存储
    return file_path


def delete_file(file_path: str) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        是否删除成功
    """
    try:
        if settings.STORAGE_TYPE == "local":
            # 从 URL 中提取实际路径
            if file_path.startswith("/uploads/"):
                relative_path = file_path[9:]  # 移除 "/uploads/"
                full_path = os.path.join(settings.LOCAL_STORAGE_PATH, relative_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    return True
        elif settings.STORAGE_TYPE == "oss":
            # TODO: 实现 OSS 删除
            pass
        
        return False
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False
