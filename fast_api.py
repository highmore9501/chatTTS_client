from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import time
import subprocess
from datetime import datetime
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import torchaudio
import ChatTTS
import torch

app = FastAPI()


class TextToWavRequest(BaseModel):
    texts: List[str]
    task_id: str  # 添加一个任务ID


class TextToWavResponse(BaseModel):
    wav: FileResponse
    lip_sync_data: FileResponse


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
    return output_file


@app.post("/text-to-wav-and-lip-sync", response_model=TextToWavResponse)
async def text_to_wav_and_lip_sync(request: TextToWavRequest):
    # Generate unique filenames based on the timestamp
    unique_filename = request.task_id
    wav_file_name = f'static/{unique_filename}.wav'
    lip_sync_data_file_name = f'static/{unique_filename}.json'

    # Convert text to WAV
    wav = text_to_wav(request.texts)

    # Save the WAV file
    torchaudio.save(wav_file_name, torch.from_numpy(wav), 24000)

    # Convert WAV to lip sync data
    wav_to_lip_sync_data(wav_file_name, lip_sync_data_file_name)

    # Return FileResponse for the WAV and lip sync data
    return TextToWavResponse(
        wav=FileResponse(path=wav_file_name, media_type="audio/wav"),
        lip_sync_data=FileResponse(
            path=lip_sync_data_file_name, media_type="application/json")
    )

# For serving static files like WAV and JSON

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8899)


"""
curl -X POST "http://localhost:8899/text-to-wav-and-lip-sync" -H "accept: application/json" -d '{"texts": ["PUT YOUR TEXT HERE"], "timestamp": "20230401-120000"}'
"""
