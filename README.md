# ai
不需要花钱的AI对话插件，星乃hoshino插件

默认的回复概率为0，启用本插件后请记得调整AI概率

例：`调整AI概率 10`，这样就有10%了

记得在`__bot__.py`里给你家bot取个名字哦，听到自己名字bot必定回复

## 介绍

如果想花钱提升AI智力，可以去申请腾讯和图灵的密钥(要钱的)，不然默认从青云客(免费，不用填密钥)获取

加了一个反并发，这个需要[反并发插件](https://github.com/lhhxxxxx/hoshino_tool)

还加了一个反[eqa](https://github.com/pcrbot/erinilis-modules/tree/master/eqa)的并发，如果没装eqa就在`setting.py`里把`eqa_db_dir`那行改为`eqa_db_dir = ""`

## 安装指南
安装依赖`pip install retrying`

在`hoshino/modules/`的目录中克隆本插件`git clone https://github.com/joeyHXD/ai.git`

在`hoshino`的目录中加入[反并发`tool.py`](https://github.com/lhhxxxxx/hoshino_tool),注意是在hoshino目录下面，不是modules

在 `HoshinoBot\hoshino\config\__bot__.py` 文件的 `MODULES_ON` 加入 `ai,`，反并发不需要改`__bot__.py`

然后重启 HoshinoBot，并在想要使用的QQ群里输入指令 `启用 ai`和`调整AI概率 10`

如果没问题的话应该就是能用了，如果有什么想要调整的内容就去setting.py里看看

## 注意
默认的AI攻击性挺强的(配合[祖安宝典](https://github.com/zangxx66/zuanDictionary)使用效果更好,乐)

如果反并发有TypeError: 'NoneType' object is not iterable，就去tool.py里改这一段
![image](https://user-images.githubusercontent.com/68325229/195911092-1c386757-75ef-4795-b5c9-6f4124156e72.png)

去掉原本的service_funcs.extend(t.find_handler(event))，改成这三行应该就行了

`handle = t.find_handler(event)`

和`if handle:` `service_funcs.extend(handle)`

注意缩进

##
特别感谢一下@雨中流浪汗大佬的帮助，帮我改了不少代码
