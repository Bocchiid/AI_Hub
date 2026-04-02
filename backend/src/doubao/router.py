# src/doubao/router.py

from fastapi import APIRouter, Depends, File, UploadFile, Form
from . import schemas as doubao_schemas
from . import model as doubao_model
from src.utils.auth import get_current_user_id
from fastapi.responses import StreamingResponse
import base64
from typing import List, Optional


router = APIRouter(
    tags = ['doubao Chat']
)

# chat without stream response
@router.post("/plain-chat", response_model = doubao_schemas.ChatResponse)
async def create_plain_chat_request(request_body: doubao_schemas.ChatRequestBody,
                                    user_id: str = Depends(get_current_user_id)):
    request = doubao_schemas.ChatRequest(
        prompt = request_body.prompt,
        user_id = user_id,
        conversation_id = request_body.conversation_id
    )

    response = await doubao_model.generate_plain_chat_response(request)
    return doubao_schemas.ChatResponse(
        response = response,
        conversation_id = request.conversation_id if request.conversation_id else None
    )

# chat with stream response
@router.post("/stream-chat")
async def create_stream_chat_request(request_body: doubao_schemas.ChatRequestBody,
                                     user_id: str = Depends(get_current_user_id)):
    """
    Server-Sent Events(SSE)
    """
    request = doubao_schemas.ChatRequest(
        prompt=request_body.prompt,
        user_id=user_id,
        conversation_id=request_body.conversation_id
    )

    stream_response, conversation_id = await doubao_model.generate_stream_chat_response(request, "You are a helpful assistant")
    headers = dict()

    if conversation_id:
        headers['conversation_id'] = conversation_id

    return StreamingResponse(
        stream_response,
        media_type = "text/event-stream",
        headers = headers
    )


@router.get("/chat-history-list", response_model = doubao_schemas.ChatHistoryListResponse)
async def get_chat_history_list(user_id: str = Depends(get_current_user_id)):
    chat_history_list_query = doubao_schemas.ChatHistoryListQuery(
        user_id = user_id
    )

    chat_history_list = await doubao_model.get_chat_history_list(chat_history_list_query)
    return doubao_schemas.ChatHistoryListResponse(
        chat_history_list = chat_history_list
    )


@router.get("/{conversation_id}")
async def get_chat_history(conversation_id: str,
                           user_id: str = Depends(get_current_user_id)):
    chat_history_query = doubao_schemas.ChatHistoryQuery(
        user_id = user_id,
        conversation_id = conversation_id
    )

    title, chat_history = await doubao_model.get_chat_history(chat_history_query)
    return doubao_schemas.ChatHistoryResponse(
        title = title,
        chat_history = chat_history
    )


# prompt to image without stream response
@router.post("/prompt-to-image", response_model = doubao_schemas.PromptToImageResponse)
async def create_prompt_to_image_request(request_body: doubao_schemas.PromptToImageRequestBody,
                                    user_id: str = Depends(get_current_user_id)):
    prompt_to_image_request = doubao_schemas.PromptToImageRequest(
        prompt = request_body.prompt,
        user_id = user_id,
        conversation_id = request_body.conversation_id
    )

    response = await doubao_model.generate_prompt_to_image_response(prompt_to_image_request)
    return doubao_schemas.PromptToImageResponse(
        img_urls = response,
        conversation_id = prompt_to_image_request.conversation_id if prompt_to_image_request.conversation_id else None
    )


# image to image without stream response
@router.post("/image-to-image", response_model = doubao_schemas.ImageToImageResponse)
async def create_image_to_image_request(prompt: str = Form(...),
                                    images: List[UploadFile] = File(...),
                                    conversation_id: Optional[str] = Form(None),
                                    user_id: str = Depends(get_current_user_id)):
    # 将上传的文件转换为 base64 字符串列表，以便传递给 model 层
    base64_images = []
    for image in images:
        content = await image.read()
        base64_str = base64.b64encode(content).decode("utf-8")
        # 组装 Data URI
        data_uri = f"data:{image.content_type};base64,{base64_str}"
        base64_images.append(data_uri)

    image_to_image_request = doubao_schemas.ImageToImageRequest(
        prompt = prompt,
        images = base64_images,
        user_id = user_id,
        conversation_id = conversation_id
    )

    response = await doubao_model.generate_image_to_image_response(image_to_image_request)
    return doubao_schemas.ImageToImageResponse(
        img_urls = response,
        conversation_id = image_to_image_request.conversation_id if image_to_image_request.conversation_id else None
    )
