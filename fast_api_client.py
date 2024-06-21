import requests
import json
import uuid
import time

host = "http://192.168.31.99:8899"
endpoint = "generate-reply"
url = f"{host}/{endpoint}"
headers = {"accept": "application/json"}

if __name__ == "__main__":
    start_time = time.time()
    userMessages = "请问海南岛的面积有多大？"
    systemPrompt = "你是一个ai助手，帮助人们解答各种问题"
    data = {
        "userMessages": userMessages,
        "systemPrompt": systemPrompt
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    wav_info = response.json()['wav_url']
    wav_url = f'{host}/static/{wav_info}'
    print(wav_url)
    lip_sync_data_info = response.json()['lip_sync_data_url']
    lip_sync_data_url = f'{host}/static/{lip_sync_data_info}'
    print(lip_sync_data_url)

    ai_reply = response.json()['ai_reply']
    print(ai_reply)

    # 下载wav文件
    wav_response = requests.get(wav_url)
    print(wav_response.content[:100])
    with open(f'output/{wav_info}', 'wb') as f:
        f.write(wav_response.content)

    # 下载lip_sync_data文件
    lip_sync_data_response = requests.get(lip_sync_data_url)
    with open(f'output/{lip_sync_data_info}', 'wb') as f:
        f.write(lip_sync_data_response.content)

    end_time = time.time()
    print(f'本次一共{len(ai_reply)}个字，生成语音和嘴唇动画消耗时间为{end_time - start_time}秒')
