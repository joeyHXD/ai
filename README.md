# ai
不需要花钱的AI对话插件，星乃hoshino插件

默认的回复概率为0，启用本插件后请记得调整AI概率

例：`调整AI概率 10`，这样就有10%了

记得在`__bot__.py`里给你家bot取个名字哦，听到自己名字bot必定回复

## 介绍
把真寻的AI对话功能和星乃的[AI对话插件](https://github.com/pcrbot/aichat)缝了起来

如果想花钱提升AI智力，可以去申请腾讯和图灵的密钥(要钱的)，不然默认从青云客(免费，不用填密钥)获取

缝了一个反并发，这个可能需要更新新版hoshino，我不确定

缝了一个反[eqa](https://github.com/pcrbot/erinilis-modules/tree/master/eqa)的并发

因为缝了很多东西，有些代码可能可以删掉，但是我没仔细研究

## 安装指南
在hoshino/module/的牡蛎中克隆本插件`git clone https://github.com/joeyHXD/ai.git`

在 `HoshinoBot\hoshino\config\__bot__.py` 文件的 `MODULES_ON` 加入 `ai,`

然后重启 HoshinoBot，并在想要使用的QQ群里输入指令 `启用 ai`和`调整AI概率 10`

如果没问题的话应该就是能用了，如果有什么想要调整的内容就去setting.py里看看

## 注意
默认的AI攻击性挺强的(配合[祖安宝典](https://github.com/zangxx66/zuanDictionary)使用效果更好,乐)
