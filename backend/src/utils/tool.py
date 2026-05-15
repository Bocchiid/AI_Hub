# src/utils/tool.py

from bson import ObjectId
import os
import shutil
import time
from fastapi import UploadFile, HTTPException

UPLOAD_ROOT = "static"


def obj():
    return str(ObjectId())


async def upload_file(file: UploadFile, sub_dir: str, allowed_types: list = None):
    """
    保存上传的文件到指定目录
    :param file: 上传的文件对象
    :param sub_dir: 子目录
    :param allowed_types: 允许的 MIME 类型列表，例如 ["image/jpeg", "image/png"]
    """
    # 1. 类型检查
    if allowed_types and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} not allowed. Supported: {allowed_types}"
        )

    # 2. 确保目录存在
    full_dest_path = os.path.join(UPLOAD_ROOT, sub_dir)
    if not os.path.exists(full_dest_path):
        os.makedirs(full_dest_path)

    # 3. 构造文件名 (保留原文件名并加上毫秒级时间戳，防止同目录重名)
    base_name, extension = os.path.splitext(file.filename)
    timestamp = int(time.time() * 1000)
    new_filename = f"{base_name}_{timestamp}{extension}"

    # 4. 构造完整保存路径
    file_path = os.path.join(full_dest_path, new_filename)

    # 5. 写入本地文件
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 6. 返回 Web 访问路径
    web_path = f'/{UPLOAD_ROOT}/{sub_dir}/{new_filename}'
    return web_path.replace("//", "/")


def remove_file(file_url: str):
    """
    根据 URL 删除本地文件
    """
    if not file_url:
        return False

    # 安全检查：只允许删除 static 目录下的文件
    if not file_url.startswith(f"/{UPLOAD_ROOT}/"):
        return False

    # 将 Web 路径转为本地相对路径 (去掉开头的 /)
    local_path = file_url.lstrip('/')

    if os.path.exists(local_path):
        try:
            os.remove(local_path)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    return False

def remove_directory(sub_dir: str):
    """
    删除整个子目录 (例如 static/experience/1715760000)
    """
    if not sub_dir:
        return
    full_path = os.path.join(UPLOAD_ROOT, sub_dir)
    if os.path.exists(full_path) and os.path.isdir(full_path):
        try:
            shutil.rmtree(full_path)
            return True
        except Exception as e:
            print(f"Error deleting directory: {e}")
            return False
    return False

import base64
def file_to_base64(file_path: str):
    """
    读取本地文件并转换为 base64 字符串
    """
    # 处理开头的 /
    if file_path.startswith('/'):
        file_path = file_path.lstrip('/')
        
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error converting file to base64: {e}")
        return None
