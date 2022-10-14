import random
from hoshino.tool import anti_conflict
from hoshino import Service
from .data_source import get_chat_result,no_result,Config
from hoshino.config import NICKNAME
import os
from .setting import DEFAULT_AI_CHANCE,BANNED_WORD,Keywords,BLACK_WORD
from . import utils

file_name = 'config.json' 
CONFIG_PATH = os.path.join(os.path.dirname(__file__), file_name)

NICKNAME_list = []
if type(NICKNAME) == str:
    NICKNAME_list.append(NICKNAME)
else:
    NICKNAME_list = list(NICKNAME)
Keywords.extend(NICKNAME_list)

ai_chance = Config(CONFIG_PATH)

sv = Service('ai')

@sv.on_prefix(('调整AI概率'))
async def enable_aichat(bot, ev):
    s = ev.message.extract_plain_text()
    if s:
        if s.isdigit() and 0<=int(s)<51:
            chance = int(s)
        else:
            await bot.finish(ev, '参数错误: 请输入0-50之间的整数.')
    else:
        chance = DEFAULT_AI_CHANCE     # 后面不接数字时调整为默认概率
    ai_chance.set_chance(str(ev.group_id), chance)
    await bot.send(ev, f'人工智障已启用, 当前bot回复概率为{chance}%.')

@sv.on_fullmatch('当前AI概率')
async def enable_aichat(bot, ev):
    try:
        chance = ai_chance.chance[str(ev.group_id)]
    except:
        chance = 0
    await bot.send(ev, f'当前bot回复概率为{chance}%.')

@sv.on_message('group')
@anti_conflict
async def ai_chat(bot, ev):
    if str(ev.group_id) not in ai_chance.chance:
        return
    text = str(ev['message'])
    msg = ev['message'].extract_plain_text().strip()
    contains_keyword = False
    if not msg:
    #没有文字，比如只是照片
        return
    if msg in utils.get_eqa_question_list(ev):
    #防止和EQA冲突
        return
    for word in BLACK_WORD:
    #防止和clanbattle以及其他原生指令冲突
        if word in msg:
            return
    if f'[CQ:at,qq={ev["self_id"]}]' in text:
    #如果被艾特，则必定触发
        contains_keyword = True
    for words in Keywords:
    #如果被提到了关键字，则必定触发
        if words in msg:
            if words in NICKNAME_list:
                msg = msg.replace(NICKNAME_list[0],"菲菲")
            contains_keyword = True
    if not contains_keyword and not random.randint(1,100) <= int(ai_chance.chance[str(ev.group_id)]):
    #roll触发概率
        return
    qq=str(ev.user_id)
    #获取对象昵称
    info = await bot.get_group_member_info(
                group_id=int(ev.group_id), user_id=int(qq)
            )
    username = info.get("card", "") or info.get("nickname", "")
    result = await get_chat_result(msg, qq, username)
    sv.logger.info(
        f"问题：{msg} ---- 回答：{result}"
    )
    if result:
        result = str(result)
        for t in BANNED_WORD:
            result = result.replace(t, "*")
        await bot.send(ev, result)
    else:
        await bot.send(ev,no_result())