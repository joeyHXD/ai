import os
import random
import re
from hoshino import R
from .utils import ai_message_manager
from hoshino.config import NICKNAME
import hoshino
from typing import Dict, Union, Optional,Any
from hoshino.config import RES_DIR
from httpx import Response
from retrying import retry
import httpx
from nonebot import MessageSegment
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from .setting import *
try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.nlp.v20190408 import nlp_client, models
except: 
    print('tx寄了/没找到密钥')

url = "http://openapi.tuling123.com/openapi/api/v2"

check_url = "https://v2.alapi.cn/api/censor/text"

index = 0

data_name = 'anime.json' 
DATA_PATH = os.path.join(os.path.dirname(__file__), data_name)
anime_data = json.load(open(DATA_PATH, "r", encoding="utf8"))
zai = os.path.join(os.path.expanduser(RES_DIR), 'img', 'zai')
noresult = os.path.join(os.path.expanduser(RES_DIR), 'img', 'noresult')

async def get_chat_result(text: str, user_id: int, nickname: str) -> str:
    """
    获取 AI 返回值，顺序： 特殊回复 -> 图灵 -> 青云客
    :param text: 问题
    :param img_url: 图片链接
    :param user_id: 用户id
    :param nickname: 用户昵称
    :return: 回答
    """
    global index
    ai_message_manager.add_message(user_id, text)
    special_rst = await ai_message_manager.get_result(user_id, nickname)
    if special_rst:
        ai_message_manager.add_result(user_id, special_rst)
        return special_rst
    if len(text) < 6 and random.random() < 0.6:
        keys = anime_data.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(anime_data[key]).replace("你", nickname)
    rst = await tu_ling(text,user_id)
    if not rst:
        rst = await xie_ai(text)
    try:
        if not rst:
            rst =  tencent_ai(text)
    except:
        rst = None
    if not rst:
        return no_result()
    
    if nickname:
        if len(nickname) < 5:
            if random.random() < 0.5:
                nickname = "~".join(nickname) + "~"
                if random.random() < 0.2:
                    if nickname.find("大人") == -1:
                        nickname += "大~人~"
        rst = str(rst).replace("小主人", nickname).replace("小朋友", nickname)
    ai_message_manager.add_result(user_id, rst)
    return rst


# 图灵接口
async def tu_ling(text: str, user_id: int) -> str:
    """
    获取图灵接口的回复
    :param text: 问题
    :param img_url: 图片链接
    :param user_id: 用户id
    :return: 图灵回复
    """
    global index
    req = None
    if TL_KEY == '' or not TL_ON:
        return ""
    try:
        req = {
                "perception": {
                    "inputText": {"text": text},
                    "selfInfo": {
                        "location": {"city": "陨石坑", "province": "火星", "street": "第5坑位"}
                    },
                },
                "userInfo": {"apiKey": TL_KEY, "userId": str(user_id)},
            }
    except IndexError:
        index = 0
        return ""
    text = ""
    response = await AsyncHttpx.post(url, json=req)
    if response.status_code != 200:
        return no_result()
    resp_payload = json.loads(response.text)
    if int(resp_payload["intent"]["code"]) in [4003]:
        return ""
    if resp_payload["results"]:
        for result in resp_payload["results"]:
            if result["resultType"] == "text":
                text = result["values"]["text"]
                if "请求次数超过" in text:
                    text = ""
    return text


# 屑 AI
bad_words = ["taobao.com","淘宝","公众号",'qq','www.']
replace_nickname = ["菲菲","艳儿"]
async def xie_ai(text: str) -> str:
    """
    获取青云客回复
    :param text: 问题
    :return: 青云可回复
    """
    res = await AsyncHttpx.get(f"http://api.qingyunke.com/api.php?key=free&appid=0&msg={text}")
    content = ""
    try:
        data = json.loads(res.text)
        if data["result"] == 0:
            content = data["content"]
            for nick_name in replace_nickname:
                if nick_name in content:
                    content = content.replace(nick_name, NICKNAME)
                    print(NICKNAME)
            for bad_word in bad_words:
                if bad_word in content:
                    return ''
            if "{br}" in content:
                content = content.replace("{br}", "\n")
            if "提示" in content:
                content = content[: content.find("提示")]
            while True:
                r = re.search("{face:(.*)}", content)
                if r:
                    id_ = r.group(1)
                    content = content.replace(
                        "{" + f"face:{id_}" + "}", str(face(int(id_)))
                    )
                else:
                    break
        return (
            content
            if not content or not ALAPI_ON
            else await check_text(content)
        )
    except Exception as e:
        hoshino.logger.warning(f"Ai xie_ai 发生错误 {type(e)}：{e}")
        return ""

def tencent_ai(text: str):
    if not TENCENT_ON:
        return ""
    elif SecretId == '' or SecretKey == '':
        return ""
    try:
        cred = credential.Credential(SecretId, SecretKey) 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "nlp.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile) 

        req = models.ChatBotRequest()
        params = {
            "Query": text,
        }
        req.from_json_string(json.dumps(params))

        resp = client.ChatBot(req)
        param = resp.to_json_string()
        reply = json.loads(param)
        msg = reply['Reply']
        return msg
    except:
        return ""
# 没有回答时回复内容
def no_result() -> str:
    """
    没有回答时的回复
    """
    return (
        random.choice(
            [
                "你在说啥子？",
                f"纯洁的{NICKNAME}没听懂",
                "下次再告诉你(下次一定)",
                "你觉得我听懂了吗？嗯？",
                "我！不！知！道！",
                '我现在还不太明白你在说什么呢，但没关系，以后的我会变得更强呢！',
                '我有点看不懂你的意思呀，可以跟我聊些简单的话题嘛',
                '其实我不太明白你的意思……',
                '抱歉哦，我现在的能力还不能够明白你在说什么，但我会加油的～',
                '唔……等会再告诉你'
            ]
        )
        + str(R.img(f'noresult/{random.choice(os.listdir(noresult))}').cqcode)
    )


async def check_text(text: str) -> str:
    """
    ALAPI文本检测，主要针对青云客API，检测为恶俗文本改为无回复的回答
    :param text: 回复
    """
    if ALAPI_TOKEN == '' or not ALAPI_ON:
        return text
    params = {"token": ALAPI_TOKEN, "text": text}
    try:
        data = (await AsyncHttpx.get(check_url, timeout=2, params=params)).json()
        if data["code"] == 200:
            if data["data"]["conclusion_type"] == 2:
                return ""
    except Exception as e:
        hoshino.logger.warning(f"检测违规文本错误...{type(e)}：{e}")
    return text

def face(id_: int) -> MessageSegment:
    """
    说明：
        生成一个 MessageSegment.face 消息
    参数：
        :param id_: 表情id
    """
    return MessageSegment.face(id_)

class Config:
    chance = {}

    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf8') as config_file:
                    self.chance = json.load(config_file)
            else:
                self.chance = {}
        except:
            self.chance = {}

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf8') as config_file:
            json.dump(self.chance, config_file, ensure_ascii=False, indent=4)

    def set_chance(self, gid, chance):
        self.chance[gid] = chance
        self.save_config()

    def delete_chance(self, gid):
        if gid in self.chance:
            del self.chance[gid]
            self.save_config()

SYSTEM_PROXY: Optional[str] = None  # 全局代理

user_agent = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    # iPhone 6：
    "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25",
]


def get_user_agent():
    return {"User-Agent": random.choice(user_agent)}
def get_local_proxy():
    """
    说明：
        获取 config.py 中设置的代理
    """
    return SYSTEM_PROXY if SYSTEM_PROXY else None

class AsyncHttpx:

    proxy = {"http://": get_local_proxy(), "https://": get_local_proxy()}

    @classmethod
    @retry(stop_max_attempt_number=3)
    async def get(
        cls,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        use_proxy: bool = True,
        proxy: Dict[str, str] = None,
        timeout: Optional[int] = 30,
        **kwargs,
    ) -> Response:
        """
        说明：
            Get
        参数：
            :param url: url
            :param params: params
            :param headers: 请求头
            :param cookies: cookies
            :param use_proxy: 使用默认代理
            :param proxy: 指定代理
            :param timeout: 超时时间
        """
        if not headers:
            headers = get_user_agent()
        proxy = proxy if proxy else cls.proxy if use_proxy else None
        async with httpx.AsyncClient(proxies=proxy) as client:
            return await client.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs
            )

    @classmethod
    async def post(
        cls,
        url: str,
        *,
        data: Optional[Dict[str, str]] = None,
        content: Any = None,
        files: Any = None,
        use_proxy: bool = True,
        proxy: Dict[str, str] = None,
        json: Optional[Dict[str, Union[Any,Any]]] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = 30,
        **kwargs,
    ) -> Response:
        """
        说明：
            Post
        参数：
            :param url: url
            :param data: data
            :param content: content
            :param files: files
            :param use_proxy: 是否默认代理
            :param proxy: 指定代理
            :param json: json
            :param params: params
            :param headers: 请求头
            :param cookies: cookies
            :param timeout: 超时时间
        """
        if not headers:
            headers = get_user_agent()
        proxy = proxy if proxy else cls.proxy if use_proxy else None
        async with httpx.AsyncClient(proxies=proxy) as client:
            return await client.post(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )