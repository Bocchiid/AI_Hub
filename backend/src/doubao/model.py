# src/doubao/model.py

from fastapi import HTTPException, status
from . import schemas as doubao_schemas
from src.core.config import DOUBAO_API_KEY, DOUBAO_MODEL, DOUBAO_IMAGE_MODEL
from src.database.mongodb import db
from src.database import aichat_repo
from src.utils.tool import obj
from openai import AsyncOpenAI


DoubaoChatHistoryCollection = db["DoubaoChatHistory"]

client = AsyncOpenAI(
    api_key= DOUBAO_API_KEY,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)


async def generate_chat_title(first_prompt: str):
    prompt_messages = [
        {"role": "system",
         "content": "你是一位专业的标题生成助手。请根据用户提供的第一句提示词，生成一个简洁、准确的标题，根据用户的提示词语言限制在10个字以内，仅返回标题，不要有其他解释。"},
        {"role": "user", "content": f"请为以下提示词生成标题：{first_prompt}"}
    ]

    response = await client.chat.completions.create(
        model = DOUBAO_MODEL,
        messages = prompt_messages,
        stream = False
    )

    return response.choices[0].message.content.strip()


async def generate_plain_chat_response(request: doubao_schemas.ChatRequest):
    if not request.conversation_id:
        request.conversation_id = obj()
        title = await generate_chat_title(request.prompt)

    doc = await aichat_repo.query_chat_history(DoubaoChatHistoryCollection,
                                                            request.user_id,
                                                            request.conversation_id)
    if doc:
        doc_data = doc[0]
        history_messages = doc_data.get('messages')
        title = doc_data.get('title')
    else:
        history_messages = []
    history_messages.append({"role": "user", "content": request.prompt})

    messages = [{"role": "system", "content": "You are a helpful assistant"}]
    messages.extend(history_messages)

    response = await client.chat.completions.create(
        model = DOUBAO_MODEL,
        messages = messages,
        stream = False
    )
    reply = response.choices[0].message.content

    history_messages.append({
        "role": "assistant", "content": reply
    })

    await aichat_repo.upsert_chat_history(DoubaoChatHistoryCollection,
                                          request.user_id,
                                          request.conversation_id,
                                          title,
                                          history_messages)

    # print(reply)
    return reply


async def generate_stream_chat_response(request: doubao_schemas.ChatRequest,
                                        system_prompt: str):
    if not request.conversation_id:
        request.conversation_id = obj()
        title = await generate_chat_title(request.prompt)

    doc = await aichat_repo.query_chat_history(DoubaoChatHistoryCollection,
                                               request.user_id,
                                               request.conversation_id)
    if doc:
        doc_data = doc[0]
        history_messages = doc_data.get('messages')
        title = doc_data.get('title')
    else:
        history_messages = []
    history_messages.append({"role": "user", "content": request.prompt})

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history_messages)

    response = await client.chat.completions.create(
        model = DOUBAO_MODEL,
        messages = messages,
        stream = True
    )

    reply = ""

    async def stream_response():
        nonlocal reply
        async for chunk in response:
            content = chunk.choices[0].delta.content

            if content:
                reply += content

                yield f"data: {content}\n\n"

        history_messages.append({
            "role": "assistant", "content": reply
        })

        await aichat_repo.upsert_chat_history(DoubaoChatHistoryCollection,
                                              request.user_id,
                                              request.conversation_id,
                                              title,
                                              history_messages)

    return stream_response(), request.conversation_id


async def get_chat_history_list(chat_history_list_request: doubao_schemas.ChatHistoryListQuery):
    raw_ls = await aichat_repo.query_chat_history_list(DoubaoChatHistoryCollection,
                                                       chat_history_list_request.user_id)

    ls = [{
        'title': item.get('title'),
        'conversation_id': item.get('_id')
    } for item in raw_ls]

    return ls


async def get_chat_history(chat_history_query: doubao_schemas.ChatHistoryQuery):
    raw_ls = await aichat_repo.query_chat_history(DoubaoChatHistoryCollection,
                                                  chat_history_query.user_id,
                                                  chat_history_query.conversation_id)

    if not raw_ls:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Not authorized to access this conversation'
        )

    title = raw_ls[0].get('title')
    chat_history = raw_ls[0].get('messages')

    return title, chat_history


async def generate_chat_generate_single_image_response(chat_generate_single_image_request: doubao_schemas.ChatGenerateImageRequest):
    if not chat_generate_single_image_request.conversation_id:
        chat_generate_single_image_request.conversation_id = obj()
        title = await generate_chat_title(chat_generate_single_image_request.prompt)

    doc = await aichat_repo.query_chat_history(DoubaoChatHistoryCollection,
                                                            chat_generate_single_image_request.user_id,
                                                            chat_generate_single_image_request.conversation_id)
    if doc:
        doc_data = doc[0]
        history_messages = doc_data.get('messages')
        title = doc_data.get('title')
    else:
        history_messages = []
    history_messages.append({"role": "user", "content": chat_generate_single_image_request.prompt})

    single_image_response = await client.images.generate(
        # Replace with Model ID
        model = DOUBAO_IMAGE_MODEL,
        prompt = chat_generate_single_image_request.prompt,
        size = "2K",
        response_format = "url",
        extra_body={
            "watermark": False,
        },
    )
    reply = single_image_response.data[0].url

    history_messages.append({
        "role": "assistant", "content": reply
    })

    await aichat_repo.upsert_chat_history(DoubaoChatHistoryCollection,
                                          chat_generate_single_image_request.user_id,
                                          chat_generate_single_image_request.conversation_id,
                                          title,
                                          history_messages)

    print(reply)
    return reply