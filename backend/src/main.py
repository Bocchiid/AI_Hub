# src/main.py

from fastapi import FastAPI

from .database.mongodb import test_connection
from .user.router import router as user_router
from .deepseek.router import router as deepseek_router
from .doubao.router import router as doubao_router
from .category.router import router as category_router
from .ai_link.router import router as ai_link_router
from .category.model import init_default_category

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


async def startup_events():
    # 1. 测试 MongoDB 连接
    await test_connection()
    # 2. 初始化默认分类 (Default)
    await init_default_category()


app = FastAPI(
    title = 'LLM',
    on_startup=[startup_events]
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router)
app.include_router(
    deepseek_router,
    prefix='/deepseek'
)
app.include_router(
    doubao_router,
    prefix='/doubao'
)
app.include_router(category_router)
# app.include_router(ai_link_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 允许的来源列表
    allow_credentials=True,
    allow_methods=["*"],   # 允许所有HTTP方法
    allow_headers=["*"],   # 允许所有请求头
    expose_headers=["conversation_id"] # 暴露header
)