import requests
import json
import uuid
import time

host = "http://192.168.31.99:8899"
endpoint = "text-to-wav-and-lip-sync"
url = f"{host}/{endpoint}"
headers = {"accept": "application/json"}

if __name__ == "__main__":
    start_time = time.time()
    texts = '现在，当客户端请求此端点时，它将收到两个文件作为响应，一个是WAV音频文件，另一个是JSON格式的唇同步数据文件。请注意，这种方法可能不适用于大文件，因为它可能会导致内存问题。对于大文件，建议将文件存储在服务器上并提供URL供客户端下载'
    # 生成唯一的task_id
    task_id = uuid.uuid1().hex
    data = {
        "texts": [texts],
        "task_id": task_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    wav_info = response.json()['wav_url']
    wav_url = f'{host}/static/{wav_info}'
    print(wav_url)
    lip_sync_data_info = response.json()['lip_sync_data_url']
    lip_sync_data_url = f'{host}/static/{lip_sync_data_info}'
    print(lip_sync_data_url)

    # 下载wav文件
    wav_response = requests.get(wav_url)
    with open(f'output/{task_id}.wav', 'wb') as f:
        f.write(wav_response.content)

    # 下载lip_sync_data文件
    lip_sync_data_response = requests.get(lip_sync_data_url)
    with open(f'output/{task_id}.json', 'wb') as f:
        f.write(lip_sync_data_response.content)

    end_time = time.time()
    print(f'本次一共{len(texts)}个字，生成语音和嘴唇动画消耗时间为{end_time - start_time}秒')
