import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models

from dotenv import load_dotenv
import os

load_dotenv()  # 这会自动从.env文件加载环境变量


def generateReply(userMessages, systemPrompt):
    try:
        secret_id = os.environ['TENCENT_SECRET_ID']
        secret_key = os.environ['TENCENT_SECRET_KEY']
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "hunyuan.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = hunyuan_client.HunyuanClient(
            cred, "ap-guangzhou", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.ChatCompletionsRequest()
        params = {
            "Model": "hunyuan-standard-32K",
            "Messages": [
                {
                    "Role": "system",
                    "Content": systemPrompt
                },
                {
                    "Role": "user",
                    "Content": userMessages
                }
            ],
            "TopP": 1,
            "Temperature": 1
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个ChatCompletionsResponse的实例，与请求对象对应
        resp = client.ChatCompletions(req)
        # 输出json格式的字符串回包
        if isinstance(resp, types.GeneratorType):  # 流式响应
            for event in resp:
                print(event)
        else:  # 非流式响应
            resp = json.loads(resp.to_json_string())
            content = resp['Choices'][0]['Message']['Content']
            return content

    except TencentCloudSDKException as err:
        print(err)


if __name__ == '__main__':
    systemPrompt = "你是一个ai助手，帮助人们解答各种问题"
    userMessages = "你好,请问中国的面积有多大？"
    generateReply(userMessages, systemPrompt)
