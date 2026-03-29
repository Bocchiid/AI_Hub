# src/utils/tool.py

from bson import ObjectId
import os
import shutil
import time
from fastapi import UploadFile


def obj():
    return str(ObjectId())


async def save_upload_file(file: UploadFile,
                           destination_dir: str):
    """
    保存上传的文件到指定目录，并在文件名后加时间戳防止碰撞
    """

    # 1. 确保目录存在
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # 2. 分离文件名和扩展名以插入时间戳
    base_name, extension = os.path.splitext(file.filename)
    timestamp = int(time.time())
    new_filename = f"{base_name}_{timestamp}{extension}"

    # 3. 构造完整保存路径
    file_path = os.path.join(destination_dir, new_filename)

    # 4. 写入本地文件
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. 返回相对于静态资源的访问路径
    # 注意：在 FastAPI 中通常挂载为 /static/，所以路径应该包含 /
    web_path = f'/{destination_dir}/{new_filename}'
    # 替换重复的斜线 (防止 destination_dir 自带斜线)
    return web_path.replace("//", "/")


def delete_local_file(file_url: str):
    """
    挑选目录根据文件的 Web URL 删除本地文件
    """
    if not file_url:
        return

    # 将 Web 路径转为本地相对路径 (去掉开头的 /)
    # 例如 /static/icons/xxx.png -> static/icons/xxx.png
    local_path = file_url.lstrip('/')

    if os.path.exists(local_path):
        try:
            os.remove(local_path)
            return True
        except Exception as e:
            print(f"Error deleting file {local_path}: {e}")
            return False
    return False
