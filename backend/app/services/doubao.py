"""
豆包 API 服务
调用 Seedream（图片生成）和 Seedance（视频生成）
"""
import asyncio
import httpx
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.config import settings


# 火山引擎 API 配置
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"


async def generate_image(
    task_id: str,
    model: str,
    prompt: str,
    negative_prompt: str,
    mode: str,
    ratio: str,
    resolution: str,
    num: int,
    image_url: Optional[str],
    user_id: int
):
    """
    生成图片 - 调用火山引擎 Seedream API
    
    Args:
        task_id: 任务ID
        model: 模型名称 (如: doubao-seedream-4-0-250828)
        prompt: 提示词
        negative_prompt: 反向提示词
        mode: 生成模式 (text2image, image2image)
        ratio: 图片比例
        resolution: 分辨率
        num: 生成数量
        image_url: 参考图片URL（图生图模式）
        user_id: 用户ID
    """
    try:
        print(f"[Task {task_id}] 开始生成图片...")
        print(f"  Model: {model}")
        print(f"  Prompt: {prompt}")
        print(f"  Mode: {mode}")
        
        # 构建请求体
        request_body = {
            "model": model,
            "prompt": prompt,
        }
        
        # 添加可选参数
        if negative_prompt:
            request_body["negative_prompt"] = negative_prompt
        
        # 调用火山引擎 API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/images/generations",
                headers={
                    "Authorization": f"Bearer {settings.DOUBAO_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_body,
                timeout=300.0
            )
            
            print(f"[Task {task_id}] Response: {response.status_code}")
            print(f"[Task {task_id}] Body: {response.text}")
            
            if response.status_code != 200:
                error_msg = f"API 调用失败: {response.status_code} - {response.text}"
                print(f"[Task {task_id}] {error_msg}")
                return {"success": False, "error": error_msg}
            
            result = response.json()
            print(f"[Task {task_id}] 图片生成成功")
            
            # 提取生成的图片 URL
            image_urls = []
            if "data" in result:
                for item in result["data"]:
                    if "url" in item:
                        image_urls.append(item["url"])
            
            return {
                "success": True,
                "task_id": task_id,
                "output_urls": image_urls,
                "raw_response": result
            }
            
    except Exception as e:
        error_msg = f"图片生成失败: {str(e)}"
        print(f"[Task {task_id}] {error_msg}")
        return {"success": False, "error": error_msg}


async def generate_video(
    task_id: str,
    model: str,
    prompt: str,
    negative_prompt: str,
    mode: str,
    ratio: str,
    resolution: str,
    duration: int,
    num: int,
    with_audio: bool,
    image_url: Optional[str],
    user_id: int,
    video_url: Optional[str] = None,
    audio_url: Optional[str] = None
):
    """
    生成视频 - 调用火山引擎 Seedance API (新格式)
    
    Args:
        task_id: 任务ID
        model: 模型名称 (如: doubao-seedance-2-0-260128)
        prompt: 提示词/内容描述
        negative_prompt: 反向提示词
        mode: 生成模式 (text2video, image2video, multimodal)
        ratio: 视频比例
        resolution: 分辨率
        duration: 视频时长（秒）
        num: 生成数量
        with_audio: 是否生成音频
        image_url: 参考图片URL
        user_id: 用户ID
        video_url: 参考视频URL
        audio_url: 参考音频URL
    """
    try:
        print(f"[Task {task_id}] 开始生成视频...")
        print(f"  Model: {model}")
        print(f"  Prompt: {prompt[:100]}...")
        print(f"  Mode: {mode}")
        print(f"  Duration: {duration}s")
        
        # 构建 content 数组
        content = []
        
        # 添加文本提示
        if prompt:
            content.append({
                "type": "text",
                "text": prompt
            })
        
        # 添加参考图片
        if image_url:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                },
                "role": "reference_image"
            })
        
        # 添加参考视频
        if video_url:
            content.append({
                "type": "video_url",
                "video_url": {
                    "url": video_url
                },
                "role": "reference_video"
            })
        
        # 添加参考音频
        if audio_url:
            content.append({
                "type": "audio_url",
                "audio_url": {
                    "url": audio_url
                },
                "role": "reference_audio"
            })
        
        # 构建请求体
        request_body = {
            "model": model,
            "content": content,
            "generate_audio": with_audio,
            "ratio": ratio,
            "duration": duration,
            "watermark": False
        }
        
        print(f"[Task {task_id}] Request: {json.dumps(request_body, ensure_ascii=False, indent=2)}")
        
        # 调用火山引擎 API 创建任务
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/contents/generations/tasks",
                headers={
                    "Authorization": f"Bearer {settings.DOUBAO_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_body,
                timeout=60.0
            )
            
            print(f"[Task {task_id}] Response: {response.status_code}")
            print(f"[Task {task_id}] Body: {response.text}")
            
            if response.status_code != 200:
                error_msg = f"API 调用失败: {response.status_code} - {response.text}"
                print(f"[Task {task_id}] {error_msg}")
                return {"success": False, "error": error_msg}
            
            result = response.json()
            
            # 获取任务 ID
            doubao_task_id = result.get("id")
            if not doubao_task_id:
                error_msg = "API 响应中缺少任务 ID"
                print(f"[Task {task_id}] {error_msg}")
                return {"success": False, "error": error_msg}
            
            print(f"[Task {task_id}] 视频任务创建成功，ID: {doubao_task_id}")
            
            # 轮询查询任务状态
            video_result = await _poll_video_task(client, doubao_task_id, task_id)
            
            return video_result
            
    except Exception as e:
        error_msg = f"视频生成失败: {str(e)}"
        print(f"[Task {task_id}] {error_msg}")
        return {"success": False, "error": error_msg}


async def _poll_video_task(client: httpx.AsyncClient, doubao_task_id: str, task_id: str) -> Dict[str, Any]:
    """
    轮询查询视频生成任务状态
    
    Args:
        client: HTTP 客户端
        doubao_task_id: 火山引擎任务 ID
        task_id: 本地任务 ID
    
    Returns:
        视频生成结果
    """
    max_retries = 120  # 最多轮询 120 次（10分钟）
    retry_interval = 5  # 每次间隔 5 秒
    
    for i in range(max_retries):
        try:
            response = await client.get(
                f"{BASE_URL}/contents/generations/tasks/{doubao_task_id}",
                headers={
                    "Authorization": f"Bearer {settings.DOUBAO_API_KEY}",
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"[Task {task_id}] 查询任务状态失败: {response.status_code}")
                await asyncio.sleep(retry_interval)
                continue
            
            result = response.json()
            status = result.get("status")
            
            print(f"[Task {task_id}] 任务状态: {status} (第 {i+1} 次查询)")
            
            if status == "Succeeded":
                # 任务完成，提取视频 URL
                video_urls = []
                content = result.get("content", [])
                for item in content:
                    if item.get("type") == "video_url":
                        video_url = item.get("video_url", {}).get("url")
                        if video_url:
                            video_urls.append(video_url)
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "output_urls": video_urls,
                    "raw_response": result
                }
            
            elif status == "Failed":
                # 任务失败
                error_msg = result.get("error", {}).get("message", "未知错误")
                print(f"[Task {task_id}] 视频生成失败: {error_msg}")
                return {"success": False, "error": error_msg}
            
            # 任务仍在处理中，继续轮询
            await asyncio.sleep(retry_interval)
            
        except Exception as e:
            print(f"[Task {task_id}] 查询任务状态异常: {e}")
            await asyncio.sleep(retry_interval)
    
    # 超时
    print(f"[Task {task_id}] 视频生成超时")
    return {"success": False, "error": "视频生成超时"}


async def check_task_status(task_id: str, task_type: str) -> dict:
    """
    查询任务状态
    
    Args:
        task_id: 任务ID
        task_type: 任务类型 (image, video)
    
    Returns:
        任务状态信息
    """
    # 这里可以实现查询逻辑
    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 50,
    }
