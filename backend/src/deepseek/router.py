# src/deepseek/router.py

from fastapi import APIRouter, Depends
from . import schemas as deepseek_schemas
from . import model as deepseek_model
from src.utils.auth import get_current_user_id
from fastapi.responses import StreamingResponse


router = APIRouter(
    tags = ['Deepseek Chat']
)

# chat without stream response
@router.post("/plain-chat", response_model = deepseek_schemas.ChatResponse)
async def create_plain_chat_request(request_body: deepseek_schemas.ChatRequestBody,
                                    user_id: str = Depends(get_current_user_id)):
    request = deepseek_schemas.ChatRequest(
        prompt = request_body.prompt,
        user_id = user_id,
        conversation_id = request_body.conversation_id
    )

    response = await deepseek_model.generate_plain_chat_response(request)
    return deepseek_schemas.ChatResponse(
        response = response,
        conversation_id = request.conversation_id if request.conversation_id else None
    )

# chat with stream response
@router.post("/stream-chat")
async def create_stream_chat_request(request_body: deepseek_schemas.ChatRequestBody,
                                     user_id: str = Depends(get_current_user_id)):
    """
    Server-Sent Events(SSE)
    """
    request = deepseek_schemas.ChatRequest(
        prompt=request_body.prompt,
        user_id=user_id,
        conversation_id=request_body.conversation_id
    )

    stream_response, conversation_id = await deepseek_model.generate_stream_chat_response(request, "You are a helpful assistant")
    headers = dict()

    if conversation_id:
        headers['conversation_id'] = conversation_id

    return StreamingResponse(
        stream_response,
        media_type = "text/event-stream",
        headers = headers
    )


@router.get("/chat-history-list", response_model = deepseek_schemas.ChatHistoryListResponse)
async def get_chat_history_list(user_id: str = Depends(get_current_user_id)):
    chat_history_list_query = deepseek_schemas.ChatHistoryListQuery(
        user_id = user_id
    )

    chat_history_list = await deepseek_model.get_chat_history_list(chat_history_list_query)
    return deepseek_schemas.ChatHistoryListResponse(
        chat_history_list = chat_history_list
    )


@router.get("/{conversation_id}")
async def get_chat_history(conversation_id: str,
                           user_id: str = Depends(get_current_user_id)):
    chat_history_query = deepseek_schemas.ChatHistoryQuery(
        user_id = user_id,
        conversation_id = conversation_id
    )

    title, chat_history = await deepseek_model.get_chat_history(chat_history_query)
    return deepseek_schemas.ChatHistoryResponse(
        title = title,
        chat_history = chat_history
    )