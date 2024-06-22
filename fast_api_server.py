from fastapi.staticfiles import StaticFiles
import subprocess
from typing import List
from pydantic import BaseModel
import torchaudio
import ChatTTS
import torch
from tencent import generateReply
from fastapi import FastAPI, HTTPException, BackgroundTasks
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
import os
import aiofiles
import asyncio
import io


app = FastAPI()


class RequestModel(BaseModel):
    userMessages: str
    systemPrompt: str


class TextToWavResponse(BaseModel):
    wav_url: str
    lip_sync_data_url: str
    ai_reply: str


chat = ChatTTS.Chat()
chat.load_models('local', local_path='huggingface')


def text_to_wav(texts: List[str]):
    wavs = chat.infer(texts)
    return wavs[0]


def wav_to_lip_sync_data(wav_file: str, output_file: str):
    subprocess.run([
        'Rhubarb/rhubarb',  # 确保这里是Rhubarb的正确路径
        '-r', 'phonetic',
        '-f', 'json',
        '--datUsePrestonBlair',
        '-o', output_file,
        wav_file
    ])
    print(f'Generated lip sync data at {output_file}')
    return output_file


@app.post("/generate-reply/")
async def api_generate_reply(request: RequestModel, background_tasks: BackgroundTasks):
    if not request.userMessages or not request.systemPrompt:
        raise HTTPException(
            status_code=400, detail="Both 'userMessages' and 'systemPrompt' are required and must be non-empty strings.")
    aiReply = generateReply(request.userMessages, request.systemPrompt)

    # 去掉换行符并按句号分割成多个字符串
    aiReply_sentences = aiReply.replace('\n', '').split('。')
    # 移除空字符串
    aiReply_sentences = [sentence.strip()
                         for sentence in aiReply_sentences if sentence.strip()]
    # 生成n个unique_filename
    unique_filenames = [
        f'{uuid.uuid4()}' for _ in range(len(aiReply_sentences))]

    # 先返回分割好的字符串列表和n个unique_filename给用户
    response_data = {
        'ai_reply_sentences': aiReply_sentences,
        # 仅返回文件名，不包含路径
        'unique_filenames': unique_filenames
    }

    # 使用后台任务生成wav和lip sync data
    background_tasks.add_task(
        generate_wav_and_lip_sync_data, aiReply_sentences, unique_filenames)

    return response_data


async def generate_wav_and_lip_sync_data(aiReply_sentences, unique_filenames):
    for aiReply_sentence, unique_filename in zip(aiReply_sentences, unique_filenames):
        await generate_wav_and_lip_sync_for_one(aiReply_sentence, unique_filename)


async def generate_wav_and_lip_sync_for_one(sentence, unique_filename):
    loop = asyncio.get_event_loop()
    # 异步生成 WAV
    wav = text_to_wav([sentence])
    wav_file_name = f'static/{unique_filename}.wav'
    temp_wav_file_name = f'static/tmp_{unique_filename}.wav'
    lip_sync_data_file_name = f'static/{unique_filename}.json'
    temp_sync_data_file_name = f'static/tmp_{unique_filename}.json'

    torchaudio.save(temp_wav_file_name, torch.from_numpy(wav), 24000)

    # 异步重命名为最终文件名
    await loop.run_in_executor(None, os.rename, temp_wav_file_name, wav_file_name)

    # 转换 WAV 到 lip sync 数据
    await loop.run_in_executor(None, wav_to_lip_sync_data, wav_file_name, temp_sync_data_file_name)

    # 异步重命名为最终文件名
    await loop.run_in_executor(None, os.rename, temp_sync_data_file_name, lip_sync_data_file_name)


# For serving static files like WAV and JSON


app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8899)
