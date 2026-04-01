# src/utils/tool.py

from bson import ObjectId
import os
import shutil
import time
from fastapi import UploadFile, HTTPException

UPLOAD_ROOT = "static"


def obj():
    return str(ObjectId())


async def upload_file(file: UploadFile, sub_dir: str):
    """
    保存上传的文件到指定目录，并在文件名后加时间戳
    """
    # 1. 确保目录存在
    full_dest_path = os.path.join(UPLOAD_ROOT, sub_dir)
    if not os.path.exists(full_dest_path):
        os.makedirs(full_dest_path)

    # 2. 分离文件名和扩展名以插入时间戳
    base_name, extension = os.path.splitext(file.filename)
    timestamp = int(time.time())
    new_filename = f"{base_name}_{timestamp}{extension}"

    # 3. 构造完整保存路径
    file_path = os.path.join(full_dest_path, new_filename)

    # 4. 写入本地文件
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. 返回 Web 访问路径
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
