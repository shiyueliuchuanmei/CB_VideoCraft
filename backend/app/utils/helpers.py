"""
通用工具函数
"""
import uuid
from datetime import datetime


def generate_task_id(prefix: str = "task") -> str:
    """
    生成任务ID
    
    Args:
        prefix: 前缀
    
    Returns:
        任务ID
    """
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def format_datetime(dt: datetime) -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
    
    Returns:
        格式化后的字符串
    """
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_ratio(ratio: str) -> tuple:
    """
    解析比例字符串
    
    Args:
        ratio: 比例字符串，如 "16:9"
    
    Returns:
        (宽, 高) 元组
    """
    parts = ratio.split(":")
    if len(parts) != 2:
        return (1, 1)
    try:
        w, h = int(parts[0]), int(parts[1])
        return (w, h)
    except ValueError:
        return (1, 1)


def calculate_dimensions(ratio: str, resolution: str) -> tuple:
    """
    根据比例和分辨率计算尺寸
    
    Args:
        ratio: 比例，如 "16:9"
        resolution: 分辨率，如 "1080p"
    
    Returns:
        (宽, 高) 元组
    """
    ratio_w, ratio_h = parse_ratio(ratio)
    
    # 根据分辨率确定基准边长
    if resolution.endswith("p"):
        # 视频分辨率，如 1080p 表示高度为 1080
        base_height = int(resolution[:-1])
        width = int(base_height * ratio_w / ratio_h)
        height = base_height
    else:
        # 图片分辨率，如 1024 表示宽度为 1024
        base_width = int(resolution)
        width = base_width
        height = int(base_width * ratio_h / ratio_w)
    
    # 确保尺寸为 8 的倍数（某些模型要求）
    width = (width // 8) * 8
    height = (height // 8) * 8
    
    return (width, height)


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的文件名
    """
    import re
    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制长度
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200] + ('.' + ext if ext else '')
    return filename


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
