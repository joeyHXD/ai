from hoshino.config import NICKNAME as nicknames

TL_ON = False
TL_KEY = ''

ALAPI_ON = False
ALAPI_TOKEN = ''

TENCENT_ON = False
SecretId = '' #  填你的SecretId
SecretKey = ''#  填你的SecretKey

name = 0#从元组选名字
NICKNAME = nicknames[name] if type(nicknames) == tuple else nicknames

DEFAULT_AI_CHANCE = 0
Keywords = ['bot','BOT','Bot','机器人','人工智障']
#防止和clanbattleV2，以及一些无法反并发的指令冲突
BLACK_WORD = [
    '报刀','状态','删刀','撤销','启用','禁用','预约','催刀','尾刀','建会',
    '查看公会','入会','查看成员', '成员查看', '查询成员', '成员查询','退会',
    '清空成员','一键入会','出刀','出尾刀', '收尾','出补时刀', '补时刀', '补时',
    '掉刀','挂树','上树','锁定', '申请出刀','进度','解锁','统计','查刀','lssv',
    'disable','enable'
]
#一些脏话
BANNED_WORD = (
    'rbq', 'RBQ', '憨批', '废物', '死妈', '崽种', '傻逼', '傻逼玩意',
    '没用东西', '傻B', '傻b', 'SB', 'sb', '煞笔', 'cnm', '爬', 'kkp',
    'nmsl', 'D区', '口区', '我是你爹', 'nmbiss', '弱智', '给爷爬', '杂种爬','爪巴'
)
#填eqa的数据库地址，防止冲突
eqa_db_dir = "./hoshino/modules/eqa/data/db.sqlite"