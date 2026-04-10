"""
任务模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    """生成任务表"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(64), unique=True, index=True, nullable=False)
    
    # 任务类型: image, video
    task_type = Column(String(20), nullable=False)
    
    # 任务状态: pending, processing, completed, failed, cancelled
    status = Column(String(20), default="pending")
    
    # 模型信息
    model = Column(String(100), nullable=False)
    
    # 生成参数
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, default="")
    mode = Column(String(20), default="text2image")  # text2image, image2image, text2video, image2video
    
    # 图片/视频参数
    ratio = Column(String(10), default="1:1")
    resolution = Column(String(20), default="1024")
    duration = Column(Integer, default=5)  # 视频时长（秒）
    num = Column(Integer, default=1)  # 生成数量
    with_audio = Column(Boolean, default=False)  # 是否带音效
    
    # 输入图片（图生图/图生视频）
    input_image_url = Column(Text, default="")
    
    # 输出结果
    output_urls = Column(Text, default="")  # JSON 数组
    
    # 错误信息
    error_message = Column(Text, default="")
    
    # 耗时和费用
    processing_time = Column(Float, default=0)  # 处理时间（秒）
    cost = Column(Float, default=0)  # 费用
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            "id": self.id,
            "task_id": self.task_id,
            "type": self.task_type,
            "status": self.status,
            "model": self.model,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "mode": self.mode,
            "ratio": self.ratio,
            "resolution": self.resolution,
            "duration": self.duration,
            "num": self.num,
            "with_audio": self.with_audio,
            "input_image_url": self.input_image_url,
            "output_urls": json.loads(self.output_urls) if self.output_urls else [],
            "error_message": self.error_message,
            "processing_time": self.processing_time,
            "cost": self.cost,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
