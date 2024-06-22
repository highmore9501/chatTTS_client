import requests
import json
import uuid
import time

host = "http://192.168.31.99:8899"
endpoint = "generate-reply/"
url = f"{host}/{endpoint}"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"  # 设置Content-Type为application/json
}

if __name__ == "__main__":
    start_time = time.time()
    userMessages = " 能介绍一下河马的习性吗？"
    systemPrompt = "你是一个ai助手，帮助人们解答各种问题。你的回答要简短，不要长篇大论。"
    data = {
        "userMessages": userMessages,
        "systemPrompt": systemPrompt
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    ai_reply_sentences = response.json()['ai_reply_sentences']
    unique_filenames = response.json()['unique_filenames']
    for ai_reply_sentence in ai_reply_sentences:
        print(ai_reply_sentence)

    for unique_filename in unique_filenames:
        print(unique_filename)

    end_time = time.time()
    print(f'生成回复消耗时间为{end_time - start_time}秒')
    start_time = end_time

    for unique_filename in unique_filenames:
        wav_url = f'{host}/static/{unique_filename}.wav'
        lip_sync_data_url = f'{host}/static/{unique_filename}.json'

        wav_file_downloaded = False
        lip_file_downloaded = False

        while not (wav_file_downloaded and lip_file_downloaded):
            try:
                if not lip_file_downloaded:
                    lip_sync_data_response = requests.get(lip_sync_data_url)
                    if lip_sync_data_response.status_code == 200:
                        with open(f'output/{unique_filename}.json', 'wb') as f:
                            f.write(lip_sync_data_response.content)
                        print(f'拿回了{unique_filename}的lip_sync_data文件')
                        lip_file_downloaded = True

                if not wav_file_downloaded and lip_file_downloaded:
                    wav_response = requests.get(wav_url)
                    if wav_response.status_code == 200:
                        with open(f'output/{unique_filename}.wav', 'wb') as f:
                            f.write(wav_response.content)
                        print(f'拿回了{unique_filename}的wav文件')
                        wav_file_downloaded = True

                if wav_file_downloaded and lip_file_downloaded:
                    end_time = time.time()
                    print(
                        f'拿回了{unique_filename}的wav和lip_sync_data文件，消耗时间为{end_time - start_time}秒')
                    start_time = end_time
                else:
                    raise Exception("文件还没准备好")
            except Exception as e:
                print(f"Error: {e}. Retrying...")
                time.sleep(3)
