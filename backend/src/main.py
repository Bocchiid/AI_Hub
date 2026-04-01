# src/main.py

from fastapi import FastAPI

from .database.mongodb import test_connection
from .user.router import router as user_router
from .deepseek.router import router as deepseek_router
from .doubao.router import router as doubao_router
from .ai_hub.router import router as ai_hub_router

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title = 'LLM',
    on_startup=[test_connection]
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
app.include_router(
    ai_hub_router,
    prefix='/ai_hub'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 允许的来源列表
    allow_credentials=True,
    allow_methods=["*"],   # 允许所有HTTP方法
    allow_headers=["*"],   # 允许所有请求头
    expose_headers=["conversation_id"] # 暴露header
)