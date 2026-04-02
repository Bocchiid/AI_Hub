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


async def generate_prompt_to_image_response(prompt_to_image_request: doubao_schemas.PromptToImageRequest):
    if not prompt_to_image_request.conversation_id:
        prompt_to_image_request.conversation_id = obj()
        title = await generate_chat_title(prompt_to_image_request.prompt)

    doc = await aichat_repo.query_chat_history(DoubaoChatHistoryCollection,
                                                            prompt_to_image_request.user_id,
                                                            prompt_to_image_request.conversation_id)
    if doc:
        doc_data = doc[0]
        history_messages = doc_data.get('messages')
        title = doc_data.get('title')
    else:
        history_messages = []
    
    prompt = prompt_to_image_request.prompt
    history_messages.append({"role": "user", "content": prompt})

    # 使用 AI 判断是否需要生成多图
    # 构造判断指令
    judge_prompt = f"请判断用户的输入是否包含生成多张、几张、批量、几份或明确张数（大于1）的要求。注意：单次生成最多支持 4 张图。如果是多图需求，仅输出 'multi'；否则仅输出 'single'。用户输入：'{prompt}'"
    
    try:
        judge_response = await client.chat.completions.create(
            model = DOUBAO_MODEL,
            messages = [{"role": "user", "content": judge_prompt}],
            temperature = 0
        )
        decision = judge_response.choices[0].message.content.strip().lower()
        n = 4 if 'multi' in decision else 1
    except Exception as e:
        # 降级处理：如果 AI 判断失败，回退到简单的关键词检测
        print(f"AI 判断失败: {e}")
        multi_keywords = ["多图", "几张", "多张", "4张", "四张", "批量", "两张", "三张", "2张", "3张", "一些"]
        n = 4 if any(k in prompt for k in multi_keywords) else 1

    img_urls = []
    if n > 1:
        # 参考官网 SeeDream 2.0 连贯插画/多图流式生成模式
        image_response = await client.images.generate(
            model = DOUBAO_IMAGE_MODEL,
            prompt = prompt,
            size = "2K",
            response_format = "url",
            stream = True,
            extra_body={
                "watermark": False,
                "sequential_image_generation": "auto",
                "sequential_image_generation_options": {
                    "max_images": n
                },
            },
        )
        async for event in image_response:
            if event and event.type == "image_generation.partial_succeeded":
                if event.url:
                    img_urls.append(event.url)
    else:
        # 普通单图生成
        single_res = await client.images.generate(
            model = DOUBAO_IMAGE_MODEL,
            prompt = prompt,
            size = "2K",
            n = 1,
            response_format = "url",
            extra_body={
                "watermark": False,
            },
        )
        img_urls = [data.url for data in single_res.data]
    
    # 存入历史记录时，将URL以换行符连接
    reply_content = "\n".join(img_urls)

    history_messages.append({
        "role": "assistant", "content": reply_content
    })

    await aichat_repo.upsert_chat_history(DoubaoChatHistoryCollection,
                                          prompt_to_image_request.user_id,
                                          prompt_to_image_request.conversation_id,
                                          title,
                                          history_messages)

    return img_urls

async def generate_image_to_image_response(image_to_image_request: doubao_schemas.ImageToImageRequest):
    if not image_to_image_request.conversation_id:
        image_to_image_request.conversation_id = obj()
        title = await generate_chat_title(image_to_image_request.prompt)

    doc = await aichat_repo.query_chat_history(DoubaoChatHistoryCollection,
                                                            image_to_image_request.user_id,
                                                            image_to_image_request.conversation_id)
    if doc:
        doc_data = doc[0]
        history_messages = doc_data.get('messages')
        title = doc_data.get('title')
    else:
        history_messages = []

    prompt = image_to_image_request.prompt
    # 存入历史记录时，标记为图生图，并记录参考图
    history_messages.append({
        "role": "user", 
        "content": f"[img2img: {', '.join(image_to_image_request.images)}] {prompt}"
    })

    # AI judge image count, max 4
    judge_prompt = f"Please judge if the user wants multiple images. Output 'multi' or 'single'. User input: '{prompt}'"
    
    try:
        judge_response = await client.chat.completions.create(
            model = DOUBAO_MODEL,
            messages = [{"role": "user", "content": judge_prompt}],
            temperature = 0
        )
        decision = judge_response.choices[0].message.content.strip().lower()
        n = 4 if 'multi' in decision else 1
    except Exception as e:
        print(f"AI Judge Failed: {e}")
        n = 1

    img_urls = []
    # img2img sequential generation (SeeDream 2.0)
    image_response = await client.images.generate(
        model = DOUBAO_IMAGE_MODEL,
        prompt = prompt,
        size = "2K",
        response_format = "url",
        stream = True,
        extra_body={
            "image": image_to_image_request.images, 
            "watermark": False,
            "sequential_image_generation": "auto",
            "sequential_image_generation_options": {
                "max_images": n
            },
        },
    )
    async for event in image_response:
        if event and event.type == "image_generation.partial_succeeded":
            if event.url:
                img_urls.append(event.url)

    # Save to history
    reply_content = "\n".join(img_urls)
    history_messages.append({
        "role": "assistant", "content": reply_content
    })

    await aichat_repo.upsert_chat_history(DoubaoChatHistoryCollection,
                                          image_to_image_request.user_id,
                                          image_to_image_request.conversation_id,
                                          title,
                                          history_messages)

    return img_urls
