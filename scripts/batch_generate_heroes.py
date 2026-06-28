#!/usr/bin/env python3
"""
108好汉批量生成脚本
按方法论生成：研究 → 特征表 → Prompt → 生成 → 抠图
带速率限制：每生成2个角色暂停3分钟
"""

import requests
import time
import json
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# API配置
API_URL = "https://apihub.agnes-ai.com/v1/images/generations"
API_KEY_FILE = Path(__file__).parent.parent / "doc" / "02-tempmails.top改善建议_Grok编写" / "agnes api.txt"
OUTPUT_DIR = Path(__file__).parent.parent / "pic" / "agnes_generated"
RESULT_DIR = Path(__file__).parent.parent / "pic" / "test_results"

# 确保目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# 读取API Key
API_KEY = API_KEY_FILE.read_text().strip()

# 风格描述（固定）
STYLE = """Chibi 2-head-body ratio Q-version character, Chinese ink wash and watercolor hand-drawn style, 
fine black ink outlines with soft watercolor blending, low-saturation traditional muted tones 
with subtle bright accent colors, 
Song Dynasty Chinese ancient costume details, cute office worker temperament, 
high definition, 8K quality, character design sheet style."""

# 108好汉特征数据（基于方法论：标志性年龄段 + 核心特征）
# 只包含未生成的角色
HEROES = [
    {
        "name": "关胜",
        "alias": "大刀",
        "iconic_age": "40-50岁",
        "features": "中年武将，红脸长髯（类似关羽），戴绿色头巾或武将盔甲，穿绿色战袍，手持青龙偃月刀，威严庄重",
        "prompt": "A middle-aged Chinese warrior general aged 40-50 with a red face, long flowing black beard, wearing a green warrior headscarf and green battle robe, holding a crescent moon blade, dignified and majestic expression."
    },
    {
        "name": "秦明",
        "alias": "霹雳火",
        "iconic_age": "35-45岁",
        "features": "壮年武将，面色红润，性如烈火，戴武将头盔，穿红色战袍，手持狼牙棒，勇猛彪悍",
        "prompt": "A strong Chinese warrior aged 35-45 with a ruddy face, fierce expression, wearing a warrior helmet and red battle robe, holding a wolf-tooth club, bold and fierce temperament."
    },
    {
        "name": "呼延灼",
        "alias": "双鞭",
        "iconic_age": "40-50岁",
        "features": "中年武将，面容刚毅，戴武将盔甲，穿黑色战袍，手持双鞭，沉稳老练",
        "prompt": "A middle-aged Chinese warrior general aged 40-50 with a stern resolute face, wearing dark warrior armor and black battle robe, holding twin whips, calm and experienced demeanor."
    },
    {
        "name": "花荣",
        "alias": "小李广",
        "iconic_age": "25-35岁",
        "features": "青年武将，面容英俊，气质潇洒，戴武将头巾，穿白色战袍，手持弓箭，神射手",
        "prompt": "A handsome young Chinese warrior aged 25-35 with elegant demeanor, wearing a warrior headscarf and white battle robe, holding a bow and arrow, sharpshooter气质."
    },
    {
        "name": "柴进",
        "alias": "小旋风",
        "iconic_age": "30-40岁",
        "features": "贵族公子，面容俊秀，气质高贵，戴文士巾，穿华丽锦袍，手持折扇，风度翩翩",
        "prompt": "A noble Chinese gentleman aged 30-40 with handsome features, wearing an elegant scholar hat and luxurious brocade robe, holding a folding fan, refined and graceful bearing."
    },
    {
        "name": "李应",
        "alias": "扑天雕",
        "iconic_age": "35-45岁",
        "features": "中年财主，面容富态，戴文士巾，穿锦缎长袍，手持飞刀，精明干练",
        "prompt": "A prosperous Chinese gentleman aged 35-45 with a well-fed face, wearing a scholar hat and silk robe, holding flying daggers, shrewd and capable appearance."
    },
    {
        "name": "朱仝",
        "alias": "美髯公",
        "iconic_age": "35-45岁",
        "features": "中年武将，面容英武，长髯飘逸（标志性特征），戴武将头巾，穿红色战袍，手持大刀",
        "prompt": "A heroic Chinese warrior aged 35-45 with a handsome face and long flowing beard (signature feature), wearing a warrior headscarf and red battle robe, holding a broadsword."
    },
    {
        "name": "董平",
        "alias": "双枪将",
        "iconic_age": "25-35岁",
        "features": "青年武将，面容俊朗，气质张扬，戴武将头盔，穿银色战袍，手持双枪，英勇潇洒",
        "prompt": "A dashing young Chinese warrior aged 25-35 with bold personality, wearing a warrior helmet and silver battle robe, holding twin spears, heroic and stylish."
    },
    {
        "name": "张清",
        "alias": "没羽箭",
        "iconic_age": "25-35岁",
        "features": "青年武将，面容清秀，戴武将头巾，穿青色战袍，手持飞石，灵活敏捷",
        "prompt": "A young Chinese warrior aged 25-35 with refined features, wearing a warrior headscarf and cyan battle robe, holding stone projectiles, agile and nimble."
    },
    {
        "name": "杨志",
        "alias": "青面兽",
        "iconic_age": "35-45岁",
        "features": "中年武将，面部有青色胎记（标志性特征），面容刚毅，戴武将头巾，穿黑色战袍，手持大刀，落魄英雄",
        "prompt": "A battle-scarred Chinese warrior aged 35-45 with a distinctive green birthmark on face (signature feature), wearing a warrior headscarf and black battle robe, holding a broadsword, down-on-his-luck hero."
    },
    {
        "name": "徐宁",
        "alias": "金枪手",
        "iconic_age": "30-40岁",
        "features": "中年武将，面容英武，戴武将头盔，穿金色战袍，手持金枪，技艺精湛",
        "prompt": "A skilled Chinese warrior aged 30-40 with heroic features, wearing a warrior helmet and golden battle robe, holding a golden spear, expert craftsman of weapons."
    },
    {
        "name": "索超",
        "alias": "急先锋",
        "iconic_age": "30-40岁",
        "features": "壮年武将，面色黝黑，性急如火，戴武将头盔，穿黑色战袍，手持大斧，勇猛冲阵",
        "prompt": "A dark-complexioned Chinese warrior aged 30-40 with hot temper, wearing a warrior helmet and black battle robe, holding a great axe, charging into battle fearlessly."
    },
    {
        "name": "戴宗",
        "alias": "神行太保",
        "iconic_age": "30-40岁",
        "features": "中年，面容清瘦，腿上绑神行甲马（标志性道具），穿行者装束，日行八百里",
        "prompt": "A lean Chinese traveler aged 30-40 with thin face, wearing magical running talismans on legs (signature item), dressed as a swift messenger, capable of running 800 li per day."
    },
    {
        "name": "刘唐",
        "alias": "赤发鬼",
        "iconic_age": "30-40岁",
        "features": "壮年，红色头发（标志性特征），面容凶悍，戴头巾，穿黑色短打，手持朴刀，豪迈粗犷",
        "prompt": "A fierce Chinese fighter aged 30-40 with distinctive red hair (signature feature), rugged face, wearing a headscarf and black short clothes, holding a broad blade, bold and rough."
    },
    {
        "name": "穆弘",
        "alias": "没遮拦",
        "iconic_age": "30-40岁",
        "features": "壮年武将，面容威猛，戴武将头巾，穿战袍，手持大刀，无人能挡",
        "prompt": "A powerful Chinese warrior aged 30-40 with intimidating face, wearing a warrior headscarf and battle robe, holding a broadsword, unstoppable force."
    },
    {
        "name": "雷横",
        "alias": "插翅虎",
        "iconic_age": "30-40岁",
        "features": "壮年，面容粗犷，戴头巾，穿武官服饰，手持朴刀，臂力过人",
        "prompt": "A rugged Chinese fighter aged 30-40 with rough features, wearing a headscarf and official martial attire, holding a broad blade, exceptional arm strength."
    },
    {
        "name": "李俊",
        "alias": "混江龙",
        "iconic_age": "30-40岁",
        "features": "壮年，面容精干，水性极好，戴头巾，穿水手装束，手持分水刺，水上豪杰",
        "prompt": "A capable Chinese water warrior aged 30-40 with sharp features, wearing a headscarf and sailor attire, holding a water-splitting blade, river hero."
    },
    {
        "name": "阮小七",
        "alias": "活阎罗",
        "iconic_age": "25-35岁",
        "features": "青年渔民，面容黝黑精干，戴斗笠，穿粗布短打，手持鱼叉，水上好汉",
        "prompt": "A dark-skinned young Chinese fisherman aged 25-35 with lean features, wearing a bamboo hat and coarse cloth clothes, holding a fishing harpoon, water hero."
    },
    {
        "name": "张横",
        "alias": "船火儿",
        "iconic_age": "30-40岁",
        "features": "壮年船夫，面容精悍，戴头巾，穿船夫装束，手持大刀，水上悍匪",
        "prompt": "A tough Chinese boatman aged 30-40 with fierce features, wearing a headscarf and boatman attire, holding a broadsword, river bandit."
    },
    {
        "name": "张顺",
        "alias": "浪里白条",
        "iconic_age": "25-35岁",
        "features": "青年，皮肤白皙（水中白条），面容俊朗，戴头巾，穿白色短打，手持鱼叉，水性第一",
        "prompt": "A fair-skinned young Chinese swimmer aged 25-35 with handsome features (white as fish in water), wearing a headscarf and white short clothes, holding a harpoon, best swimmer."
    },
    {
        "name": "杨雄",
        "alias": "病关索",
        "iconic_age": "30-40岁",
        "features": "中年，面色略带病容，戴头巾，穿文官服饰，手持大刀，外柔内刚",
        "prompt": "A Chinese official aged 30-40 with slightly pale complexion, wearing a headscarf and civil official attire, holding a broadsword, gentle exterior but strong inside."
    },
    {
        "name": "石秀",
        "alias": "拼命三郎",
        "iconic_age": "25-35岁",
        "features": "青年，面容精干坚毅，戴头巾，穿短打劲装，手持尖刀，拼命三郎",
        "prompt": "A determined young Chinese fighter aged 25-35 with resolute face, wearing a headscarf and tight-fitting clothes, holding a sharp blade, fearless fighter."
    },
    {
        "name": "解珍",
        "alias": "两头蛇",
        "iconic_age": "25-35岁",
        "features": "青年猎户，面容精悍，戴皮帽，穿猎户装束，手持钢叉，山中猎手",
        "prompt": "A young Chinese hunter aged 25-35 with tough features, wearing a leather cap and hunter attire, holding a steel fork, mountain hunter."
    },
    {
        "name": "解宝",
        "alias": "双尾蝎",
        "iconic_age": "25-35岁",
        "features": "青年猎户，面容凶悍，戴皮帽，穿猎户装束，手持钢叉，与兄长解珍搭档",
        "prompt": "A fierce young Chinese hunter aged 25-35 with intimidating features, wearing a leather cap and hunter attire, holding a steel fork, partnered with brother Xie Zhen."
    },
    # 地煞星
    {
        "name": "朱武",
        "alias": "神机军师",
        "iconic_age": "35-45岁",
        "features": "中年文士，面容睿智，戴文士巾，穿青色长袍，手持羽扇，军师气质",
        "prompt": "A wise Chinese strategist aged 35-45 with intelligent face, wearing a scholar hat and cyan robe, holding a feather fan, counselor demeanor."
    },
    {
        "name": "黄信",
        "alias": "镇三山",
        "iconic_age": "30-40岁",
        "features": "中年武将，面容威严，戴武将头盔，穿战袍，手持大刀，镇守三山",
        "prompt": "A dignified Chinese warrior aged 30-40 with imposing face, wearing a warrior helmet and battle robe, holding a broadsword, guardian of three mountains."
    },
    {
        "name": "孙立",
        "alias": "病尉迟",
        "iconic_age": "35-45岁",
        "features": "中年武将，面色略带病容但英武，戴武将头盔，穿战袍，手持鞭枪，沉稳老练",
        "prompt": "A Chinese warrior aged 35-45 with slightly pale but heroic face, wearing a warrior helmet and battle robe, holding a whip-spear, calm and experienced."
    },
    {
        "name": "宣赞",
        "alias": "丑郡马",
        "iconic_age": "30-40岁",
        "features": "中年武将，面容丑陋但武艺高强，戴武将头盔，穿战袍，手持大刀",
        "prompt": "An ugly but highly skilled Chinese warrior aged 30-40 with homely face, wearing a warrior helmet and battle robe, holding a broadsword."
    },
    {
        "name": "郝思文",
        "alias": "井木犴",
        "iconic_age": "30-40岁",
        "features": "中年武将，面容刚毅，戴武将头盔，穿战袍，手持长枪",
        "prompt": "A resolute Chinese warrior aged 30-40 with firm features, wearing a warrior helmet and battle robe, holding a long spear."
    },
    {
        "name": "韩滔",
        "alias": "百胜将",
        "iconic_age": "35-45岁",
        "features": "中年武将，面容威武，戴武将头盔，穿战袍，手持大刀，百战百胜",
        "prompt": "A mighty Chinese warrior aged 35-45 with powerful features, wearing a warrior helmet and battle robe, holding a broadsword, victorious in hundred battles."
    },
    {
        "name": "彭玘",
        "alias": "天目将",
        "iconic_age": "30-40岁",
        "features": "中年武将，面容英武，戴武将头盔，穿战袍，手持三尖两刃刀",
        "prompt": "A heroic Chinese warrior aged 30-40 with brave features, wearing a warrior helmet and battle robe, holding a three-pointed double-edged blade."
    },
    {
        "name": "单廷珪",
        "alias": "圣水将军",
        "iconic_age": "30-40岁",
        "features": "中年武将，面容清秀，戴武将头盔，穿蓝色战袍，精通水战",
        "prompt": "A refined Chinese warrior aged 30-40 with clean features, wearing a warrior helmet and blue battle robe, expert in water warfare."
    },
    {
        "name": "魏定国",
        "alias": "神火将军",
        "iconic_age": "30-40岁",
        "features": "中年武将，面色红润，戴武将头盔，穿红色战袍，精通火攻",
        "prompt": "A ruddy-faced Chinese warrior aged 30-40 with fiery complexion, wearing a warrior helmet and red battle robe, expert in fire attacks."
    },
    {
        "name": "萧让",
        "alias": "圣手书生",
        "iconic_age": "30-40岁",
        "features": "中年文士，面容清秀，戴文士巾，穿青色长袍，手持毛笔，书法大家",
        "prompt": "A refined Chinese scholar aged 30-40 with elegant features, wearing a scholar hat and cyan robe, holding a calligraphy brush, master calligrapher."
    },
    {
        "name": "裴宣",
        "alias": "铁面孔目",
        "iconic_age": "35-45岁",
        "features": "中年文官，面容严肃，戴官帽，穿官服，手持案卷，铁面无私",
        "prompt": "A stern Chinese official aged 35-45 with severe face, wearing an official hat and official robes, holding legal documents, incorruptible judge."
    },
    {
        "name": "欧鹏",
        "alias": "摩云金翅",
        "iconic_age": "30-40岁",
        "features": "壮年，面容精悍，戴头巾，穿战袍，手持大刀，身手敏捷",
        "prompt": "A nimble Chinese fighter aged 30-40 with sharp features, wearing a headscarf and battle robe, holding a broadsword, agile and skilled."
    },
    {
        "name": "邓飞",
        "alias": "火眼狻猊",
        "iconic_age": "30-40岁",
        "features": "壮年，眼睛红色（标志性特征），面容凶悍，戴头巾，穿战袍，手持铁链",
        "prompt": "A fierce Chinese fighter aged 30-40 with distinctive red eyes (signature feature), wearing a headscarf and battle robe, holding iron chains."
    },
    {
        "name": "燕顺",
        "alias": "锦毛虎",
        "iconic_age": "30-40岁",
        "features": "壮年，赤发黄须（标志性特征），面容凶猛，戴头巾，穿虎皮战袍",
        "prompt": "A fierce Chinese bandit aged 30-40 with red hair and yellow beard (signature features), wearing a headscarf and tiger-skin robe."
    },
    {
        "name": "杨林",
        "alias": "锦豹子",
        "iconic_age": "30-40岁",
        "features": "壮年，面容精悍，戴头巾，穿豹纹战袍，手持大刀",
        "prompt": "A tough Chinese fighter aged 30-40 with sharp features, wearing a headscarf and leopard-pattern robe, holding a broadsword."
    },
    {
        "name": "凌振",
        "alias": "轰天雷",
        "iconic_age": "30-40岁",
        "features": "中年，面容精干，戴官帽，穿工匠服饰，手持火炮图纸，火炮专家",
        "prompt": "A capable Chinese engineer aged 30-40 with sharp features, wearing an official hat and craftsman attire, holding cannon blueprints, artillery expert."
    },
    {
        "name": "蒋敬",
        "alias": "神算子",
        "iconic_age": "30-40岁",
        "features": "中年文士，面容精明，戴文士巾，穿青色长袍，手持算盘，精通算术",
        "prompt": "A shrewd Chinese scholar aged 30-40 with clever face, wearing a scholar hat and cyan robe, holding an abacus, mathematical expert."
    },
    {
        "name": "吕方",
        "alias": "小温侯",
        "iconic_age": "25-35岁",
        "features": "青年武将，面容英俊，戴束发金冠，穿红色战袍，手持方天画戟，模仿吕布",
        "prompt": "A handsome young Chinese warrior aged 25-35 with elegant features, wearing a golden crown and red battle robe, holding a painted halberd, emulating Lü Bu."
    },
    {
        "name": "郭盛",
        "alias": "赛仁贵",
        "iconic_age": "25-35岁",
        "features": "青年武将，面容英武，戴武将头盔，穿白色战袍，手持方天画戟",
        "prompt": "A heroic young Chinese warrior aged 25-35 with brave features, wearing a warrior helmet and white battle robe, holding a painted halberd."
    },
    {
        "name": "安道全",
        "alias": "神医",
        "iconic_age": "40-50岁",
        "features": "中年医者，面容慈祥，戴文士巾，穿青色长袍，手持药箱，医术高明",
        "prompt": "A kind Chinese doctor aged 40-50 with benevolent face, wearing a scholar hat and cyan robe, holding a medicine box, skilled physician."
    },
    {
        "name": "皇甫端",
        "alias": "紫髯伯",
        "iconic_age": "40-50岁",
        "features": "中年，紫色胡须（标志性特征），面容威严，戴文士巾，穿长袍，兽医专家",
        "prompt": "A dignified Chinese veterinarian aged 40-50 with distinctive purple beard (signature feature), wearing a scholar hat and robe, animal doctor."
    },
    {
        "name": "王英",
        "alias": "矮脚虎",
        "iconic_age": "30-40岁",
        "features": "矮小精悍，面容猥琐好色，戴头巾，穿短打，手持朴刀，五短身材",
        "prompt": "A short and tough Chinese fighter aged 30-40 with lecherous face, wearing a headscarf and short clothes, holding a broad blade, stocky build."
    },
    {
        "name": "扈三娘",
        "alias": "一丈青",
        "iconic_age": "20-30岁",
        "features": "青年女将，面容美丽英武，戴女将头盔，穿红色战袍，手持日月双刀，女中豪杰",
        "prompt": "A beautiful Chinese warrior woman aged 20-30 with heroic features, wearing a female warrior helmet and red battle robe, holding sun-moon twin blades, female hero."
    },
    {
        "name": "鲍旭",
        "alias": "丧门神",
        "iconic_age": "30-40岁",
        "features": "壮年，面容凶恶，戴头巾，穿黑色战袍，手持大刀，凶神恶煞",
        "prompt": "A fearsome Chinese fighter aged 30-40 with terrifying face, wearing a headscarf and black battle robe, holding a broadsword, death-dealing appearance."
    },
    {
        "name": "樊瑞",
        "alias": "混世魔王",
        "iconic_age": "30-40岁",
        "features": "壮年，面容神秘，戴道士帽，穿道袍，手持法杖，精通法术",
        "prompt": "A mysterious Chinese Daoist aged 30-40 with enigmatic face, wearing a Daoist cap and robe, holding a magic staff, skilled in sorcery."
    },
    {
        "name": "孔明",
        "alias": "毛头星",
        "iconic_age": "25-35岁",
        "features": "青年，面容英俊，戴头巾，穿战袍，手持大刀，与孔亮是兄弟",
        "prompt": "A handsome young Chinese fighter aged 25-35 with clean features, wearing a headscarf and battle robe, holding a broadsword, brother of Kong Liang."
    },
    {
        "name": "孔亮",
        "alias": "独火星",
        "iconic_age": "25-35岁",
        "features": "青年，面容粗犷，戴头巾，穿战袍，手持朴刀，与孔明是兄弟",
        "prompt": "A rugged young Chinese fighter aged 25-35 with rough features, wearing a headscarf and battle robe, holding a broad blade, brother of Kong Ming."
    },
    {
        "name": "项充",
        "alias": "八臂哪吒",
        "iconic_age": "25-35岁",
        "features": "青年，面容精悍，戴头巾，穿战袍，手持飞刀标枪，多臂善射",
        "prompt": "A nimble young Chinese fighter aged 25-35 with sharp features, wearing a headscarf and battle robe, holding flying daggers and javelins, multi-armed archer."
    },
    {
        "name": "李衮",
        "alias": "飞天大圣",
        "iconic_age": "25-35岁",
        "features": "青年，面容凶悍，戴头巾，穿战袍，手持标枪飞刀，与项充搭档",
        "prompt": "A fierce young Chinese fighter aged 25-35 with intimidating features, wearing a headscarf and battle robe, holding javelins and flying daggers, partnered with Xiang Chong."
    },
    {
        "name": "金大坚",
        "alias": "玉臂匠",
        "iconic_age": "30-40岁",
        "features": "中年工匠，面容精巧，戴文士巾，穿工匠服饰，手持刻刀，雕刻大师",
        "prompt": "A skilled Chinese craftsman aged 30-40 with delicate features, wearing a scholar hat and craftsman attire, holding a carving knife, master engraver."
    },
    {
        "name": "马麟",
        "alias": "铁笛仙",
        "iconic_age": "25-35岁",
        "features": "青年，面容清秀，戴头巾，穿青色长袍，手持铁笛，文武双全",
        "prompt": "A refined young Chinese fighter aged 25-35 with clean features, wearing a headscarf and cyan robe, holding an iron flute, skilled in both arts and martial."
    },
    {
        "name": "童威",
        "alias": "出洞蛟",
        "iconic_age": "25-35岁",
        "features": "青年渔民，面容精悍，戴斗笠，穿水手装束，手持鱼叉，水上好汉",
        "prompt": "A tough young Chinese fisherman aged 25-35 with sharp features, wearing a bamboo hat and sailor attire, holding a fishing harpoon, water hero."
    },
    {
        "name": "童猛",
        "alias": "翻江蜃",
        "iconic_age": "25-35岁",
        "features": "青年渔民，面容凶悍，戴斗笠，穿水手装束，手持鱼叉，与童威搭档",
        "prompt": "A fierce young Chinese fisherman aged 25-35 with intimidating features, wearing a bamboo hat and sailor attire, holding a fishing harpoon, partnered with Tong Wei."
    },
    {
        "name": "孟康",
        "alias": "玉幡竿",
        "iconic_age": "30-40岁",
        "features": "中年，面容清秀，戴头巾，穿工匠服饰，手持造船工具，造船专家",
        "prompt": "A refined Chinese shipwright aged 30-40 with clean features, wearing a headscarf and craftsman attire, holding shipbuilding tools, ship construction expert."
    },
    {
        "name": "侯健",
        "alias": "通臂猿",
        "iconic_age": "25-35岁",
        "features": "青年，面容瘦削，戴头巾，穿裁缝服饰，手持针线，裁缝大师",
        "prompt": "A thin Chinese tailor aged 25-35 with lean features, wearing a headscarf and tailor attire, holding needle and thread, master tailor."
    },
    {
        "name": "陈达",
        "alias": "跳涧虎",
        "iconic_age": "25-35岁",
        "features": "青年，面容凶悍，戴头巾，穿战袍，手持大刀，身手矫健",
        "prompt": "A fierce young Chinese fighter aged 25-35 with intimidating features, wearing a headscarf and battle robe, holding a broadsword, agile and athletic."
    },
    {
        "name": "杨春",
        "alias": "白花蛇",
        "iconic_age": "25-35岁",
        "features": "青年，面容阴鸷，戴头巾，穿战袍，手持大刀，与陈达搭档",
        "prompt": "A cunning young Chinese fighter aged 25-35 with sinister features, wearing a headscarf and battle robe, holding a broadsword, partnered with Chen Da."
    },
    {
        "name": "郑天寿",
        "alias": "白面郎君",
        "iconic_age": "20-30岁",
        "features": "青年，面容白净俊俏，戴头巾，穿白色长袍，手持折扇，风流倜傥",
        "prompt": "A fair-skinned handsome young Chinese gentleman aged 20-30 with clean features, wearing a headscarf and white robe, holding a folding fan, elegant and dashing."
    },
    {
        "name": "陶宗旺",
        "alias": "九尾龟",
        "iconic_age": "30-40岁",
        "features": "中年，面容朴实，戴头巾，穿农民服饰，手持锄头，庄稼好手",
        "prompt": "A simple Chinese farmer aged 30-40 with honest face, wearing a headscarf and farmer attire, holding a hoe, skilled farmer."
    },
    {
        "name": "宋清",
        "alias": "铁扇子",
        "iconic_age": "25-35岁",
        "features": "青年，面容清秀，戴文士巾，穿青色长袍，手持铁扇，宋江之弟",
        "prompt": "A refined young Chinese scholar aged 25-35 with clean features, wearing a scholar hat and cyan robe, holding an iron fan, brother of Song Jiang."
    },
    {
        "name": "乐和",
        "alias": "铁叫子",
        "iconic_age": "20-30岁",
        "features": "青年，面容清秀，戴头巾，穿文士服饰，手持乐器，精通音律",
        "prompt": "A refined young Chinese musician aged 20-30 with clean features, wearing a headscarf and scholar attire, holding a musical instrument, skilled in music."
    },
    {
        "name": "龚旺",
        "alias": "花项虎",
        "iconic_age": "25-35岁",
        "features": "壮年，脖子有纹身（标志性特征），面容粗犷，戴头巾，穿战袍",
        "prompt": "A tough Chinese fighter aged 25-35 with distinctive neck tattoos (signature feature), rugged face, wearing a headscarf and battle robe."
    },
    {
        "name": "丁得孙",
        "alias": "中箭虎",
        "iconic_age": "25-35岁",
        "features": "壮年，面容带伤疤，戴头巾，穿战袍，手持大刀，身上多处箭伤",
        "prompt": "A battle-scarred Chinese fighter aged 25-35 with scarred face, wearing a headscarf and battle robe, holding a broadsword, covered in arrow wounds."
    },
    {
        "name": "穆春",
        "alias": "小遮拦",
        "iconic_age": "25-35岁",
        "features": "青年，面容粗犷，戴头巾，穿战袍，手持朴刀，穆弘之弟",
        "prompt": "A rugged young Chinese fighter aged 25-35 with rough features, wearing a headscarf and battle robe, holding a broad blade, brother of Mu Hong."
    },
    {
        "name": "曹正",
        "alias": "操刀鬼",
        "iconic_age": "30-40岁",
        "features": "中年屠夫，面容粗犷，戴头巾，穿屠夫服饰，手持屠刀，杀猪宰羊",
        "prompt": "A tough Chinese butcher aged 30-40 with rough features, wearing a headscarf and butcher attire, holding a butcher knife, slaughtering expert."
    },
    {
        "name": "宋万",
        "alias": "云里金刚",
        "iconic_age": "30-40岁",
        "features": "壮年，身材高大，面容威猛，戴头巾，穿战袍，手持大刀",
        "prompt": "A tall and powerful Chinese fighter aged 30-40 with mighty features, wearing a headscarf and battle robe, holding a broadsword, towering presence."
    },
    {
        "name": "杜迁",
        "alias": "摸着天",
        "iconic_age": "30-40岁",
        "features": "壮年，身材高大，面容粗犷，戴头巾，穿战袍，手持大刀",
        "prompt": "A tall Chinese fighter aged 30-40 with rough features, wearing a headscarf and battle robe, holding a broadsword, reaching the sky."
    },
    {
        "name": "薛永",
        "alias": "病大虫",
        "iconic_age": "30-40岁",
        "features": "壮年，面容带病态但武艺高强，戴头巾，穿短打，手持枪棒",
        "prompt": "A Chinese fighter aged 30-40 with sickly appearance but skilled martial arts, wearing a headscarf and short clothes, holding a staff."
    },
    {
        "name": "施恩",
        "alias": "金眼彪",
        "iconic_age": "25-35岁",
        "features": "青年，眼睛金色（标志性特征），面容精干，戴头巾，穿长袍，酒店老板",
        "prompt": "A capable young Chinese innkeeper aged 25-35 with distinctive golden eyes (signature feature), wearing a headscarf and robe, tavern owner."
    },
    {
        "name": "李忠",
        "alias": "打虎将",
        "iconic_age": "30-40岁",
        "features": "壮年，面容粗犷，戴头巾，穿卖艺服饰，手持枪棒，街头卖艺",
        "prompt": "A rugged Chinese street performer aged 30-40 with rough features, wearing a headscarf and performer attire, holding a staff, street martial artist."
    },
    {
        "name": "周通",
        "alias": "小霸王",
        "iconic_age": "25-35岁",
        "features": "青年，面容凶悍，戴头巾，穿战袍，手持大刀，山大王",
        "prompt": "A fierce young Chinese bandit chief aged 25-35 with intimidating features, wearing a headscarf and battle robe, holding a broadsword, mountain king."
    },
    {
        "name": "汤隆",
        "alias": "金钱豹子",
        "iconic_age": "30-40岁",
        "features": "中年铁匠，面容黝黑，戴头巾，穿铁匠服饰，手持铁锤，打造兵器",
        "prompt": "A dark-skinned Chinese blacksmith aged 30-40 with tough features, wearing a headscarf and blacksmith attire, holding a hammer, weapons craftsman."
    },
    {
        "name": "杜兴",
        "alias": "鬼脸儿",
        "iconic_age": "30-40岁",
        "features": "中年，面容丑陋，戴头巾，穿管家服饰，精明能干",
        "prompt": "An ugly Chinese steward aged 30-40 with homely face, wearing a headscarf and steward attire, shrewd and capable."
    },
    {
        "name": "邹渊",
        "alias": "出林龙",
        "iconic_age": "30-40岁",
        "features": "壮年，面容凶悍，戴头巾，穿战袍，手持大刀，与邹润搭档",
        "prompt": "A fierce Chinese fighter aged 30-40 with intimidating features, wearing a headscarf and battle robe, holding a broadsword, partnered with Zou Run."
    },
    {
        "name": "邹润",
        "alias": "独角龙",
        "iconic_age": "30-40岁",
        "features": "壮年，头上长角（标志性特征），面容凶悍，戴头巾，穿战袍",
        "prompt": "A fierce Chinese fighter aged 30-40 with distinctive horn on head (signature feature), intimidating face, wearing a headscarf and battle robe."
    },
    {
        "name": "朱贵",
        "alias": "旱地忽律",
        "iconic_age": "30-40岁",
        "features": "中年，面容精明，戴头巾，穿商人服饰，手持算盘，酒店掌柜",
        "prompt": "A shrewd Chinese innkeeper aged 30-40 with clever face, wearing a headscarf and merchant attire, holding an abacus, tavern keeper."
    },
    {
        "name": "朱富",
        "alias": "笑面虎",
        "iconic_age": "25-35岁",
        "features": "青年，面容笑嘻嘻但心思深沉，戴头巾，穿商人服饰，笑里藏刀",
        "prompt": "A young Chinese merchant aged 25-35 with smiling face but cunning mind, wearing a headscarf and merchant attire, hiding daggers behind smile."
    },
    {
        "name": "蔡福",
        "alias": "铁臂膊",
        "iconic_age": "35-45岁",
        "features": "中年刽子手，面容冷酷，戴头巾，穿刽子手服饰，手持大刀，行刑人",
        "prompt": "A cold-faced Chinese executioner aged 35-45 with stern features, wearing a headscarf and executioner attire, holding a broadsword, headsman."
    },
    {
        "name": "蔡庆",
        "alias": "一枝花",
        "iconic_age": "30-40岁",
        "features": "中年，头戴鲜花（标志性特征），面容阴柔，戴头巾，穿刽子手服饰",
        "prompt": "A Chinese executioner aged 30-40 with distinctive flower in hair (signature feature), feminine features, wearing a headscarf and executioner attire."
    },
    {
        "name": "李立",
        "alias": "催命判官",
        "iconic_age": "30-40岁",
        "features": "中年，面容阴森，戴头巾，穿黑袍，手持生死簿，开黑店",
        "prompt": "A sinister Chinese innkeeper aged 30-40 with eerie face, wearing a headscarf and black robe, holding a life-death ledger, black inn keeper."
    },
    {
        "name": "李云",
        "alias": "青眼虎",
        "iconic_age": "30-40岁",
        "features": "中年，眼睛青色（标志性特征），面容威猛，戴头巾，穿战袍",
        "prompt": "A powerful Chinese fighter aged 30-40 with distinctive blue-green eyes (signature feature), wearing a headscarf and battle robe."
    },
    {
        "name": "焦挺",
        "alias": "没面目",
        "iconic_age": "30-40岁",
        "features": "中年，面容平凡无特征，戴头巾，穿短打，相扑高手",
        "prompt": "An ordinary-looking Chinese wrestler aged 30-40 with plain face, wearing a headscarf and short clothes, sumo wrestling expert."
    },
    {
        "name": "石勇",
        "alias": "石将军",
        "iconic_age": "30-40岁",
        "features": "壮年，面容坚毅如石，戴头巾，穿战袍，手持大刀",
        "prompt": "A rock-solid Chinese fighter aged 30-40 with stone-like resolute face, wearing a headscarf and battle robe, holding a broadsword."
    },
    {
        "name": "孙新",
        "alias": "小尉迟",
        "iconic_age": "25-35岁",
        "features": "青年，面容英武，戴头巾，穿战袍，手持大刀，孙立之弟",
        "prompt": "A heroic young Chinese fighter aged 25-35 with brave features, wearing a headscarf and battle robe, holding a broadsword, brother of Sun Li."
    },
    {
        "name": "顾大嫂",
        "alias": "母大虫",
        "iconic_age": "30-40岁",
        "features": "中年女将，面容凶悍，戴头巾，穿战袍，手持双刀，女中豪杰",
        "prompt": "A fierce Chinese warrior woman aged 30-40 with intimidating features, wearing a headscarf and battle robe, holding twin blades, female hero."
    },
    {
        "name": "张青",
        "alias": "菜园子",
        "iconic_age": "30-40岁",
        "features": "中年，面容朴实，戴头巾，穿农民服饰，手持锄头，种菜出身",
        "prompt": "A simple Chinese farmer aged 30-40 with honest face, wearing a headscarf and farmer attire, holding a hoe, vegetable gardener."
    },
    {
        "name": "孙二娘",
        "alias": "母夜叉",
        "iconic_age": "30-40岁",
        "features": "中年女将，面容凶悍泼辣，戴头巾，穿战袍，手持双刀，开黑店",
        "prompt": "A fierce Chinese warrior woman aged 30-40 with intimidating and shrewish features, wearing a headscarf and battle robe, holding twin blades, black inn keeper."
    },
    {
        "name": "王定六",
        "alias": "活闪婆",
        "iconic_age": "25-35岁",
        "features": "青年，面容精干，戴头巾，穿短打，身手敏捷，闪电般速度",
        "prompt": "A nimble young Chinese fighter aged 25-35 with sharp features, wearing a headscarf and short clothes, lightning-fast speed."
    },
    {
        "name": "郁保四",
        "alias": "险道神",
        "iconic_age": "30-40岁",
        "features": "壮年，身材高大，面容威猛，戴头巾，穿战袍，手持大旗",
        "prompt": "A tall and powerful Chinese fighter aged 30-40 with mighty features, wearing a headscarf and battle robe, holding a large banner, road-blocking god."
    },
    {
        "name": "白胜",
        "alias": "白日鼠",
        "iconic_age": "25-35岁",
        "features": "青年，面容机灵，戴头巾，穿短打，鬼鬼祟祟，小偷小摸",
        "prompt": "A sneaky young Chinese thief aged 25-35 with clever face, wearing a headscarf and short clothes, sneaky and pilfering."
    },
    {
        "name": "时迁",
        "alias": "鼓上蚤",
        "iconic_age": "25-35岁",
        "features": "青年，面容精瘦，戴头巾，穿夜行衣，手持飞爪，轻功高手",
        "prompt": "A thin young Chinese thief aged 25-35 with lean features, wearing a headscarf and night-crawler clothes, holding a grappling hook, master of lightness kung fu."
    },
    {
        "name": "段景住",
        "alias": "金毛犬",
        "iconic_age": "25-35岁",
        "features": "青年，金发（标志性特征），面容精悍，戴头巾，穿胡服，盗马贼",
        "prompt": "A young Chinese horse thief aged 25-35 with distinctive blonde hair (signature feature), wearing a headscarf and Hu-style clothing, horse rustler."
    },
]

def remove_green_background(img_path, output_path):
    """绿幕抠图"""
    img = Image.open(img_path).convert('RGBA')
    data = np.array(img)
    rgb = data[:, :, :3].astype(float)
    
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    
    green_mask = (G > 150) & (G > R * 1.3) & (G > B * 1.3)
    skin_mask = (R > 180) & (G > 100) & (B > 80) & (R > G * 0.9)
    dark_mask = (R < 60) & (G < 60) & (B < 60)
    red_mask = (R > 150) & (R > G * 1.3) & (R > B * 1.2)
    
    remove_mask = green_mask & ~skin_mask & ~dark_mask & ~red_mask
    data[remove_mask, 3] = 0
    
    result = Image.fromarray(data)
    result.save(output_path)
    
    alpha = data[:, :, 3]
    transparent_pct = (alpha < 10).sum() / alpha.size * 100
    return transparent_pct

def generate_hero(hero, max_retries=3):
    """生成单个角色（带重试）"""
    name = hero["name"]
    alias = hero["alias"]
    prompt = hero["prompt"]
    
    # 构建完整Prompt
    full_prompt = f"""{STYLE}

{prompt}

SOLID BRIGHT GREEN BACKGROUND (#00FF00), single uniform green color, no patterns, no gradients.
A calligraphy name plaque below reads "{alias}{name}" with a small red traditional Chinese seal stamp."""
    
    print(f"\n{'='*60}")
    print(f"🎭 生成: {name}（{alias}）")
    print(f"   标志性年龄: {hero['iconic_age']}")
    print(f"{'='*60}")
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"   ⏳ 重试 {attempt + 1}/{max_retries}...")
                time.sleep(30)  # 重试前等待30秒
            
            # 调用API
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "agnes-image-2.1-flash",
                    "prompt": full_prompt,
                    "n": 1,
                    "size": "1024x1024"
                },
                timeout=180  # 增加超时到3分钟
            )
            
            if response.status_code != 200:
                print(f"   ❌ API错误: {response.status_code}")
                if attempt < max_retries - 1:
                    continue
                return False
            
            # 下载图片（带重试）
            image_url = response.json()["data"][0]["url"]
            for dl_attempt in range(3):
                try:
                    img_response = requests.get(image_url, timeout=120)
                    break
                except Exception as e:
                    if dl_attempt < 2:
                        print(f"   ⏳ 下载重试 {dl_attempt + 1}/3...")
                        time.sleep(10)
                    else:
                        raise
            
            # 保存原图
            original_path = OUTPUT_DIR / f"{name}.png"
            original_path.write_bytes(img_response.content)
            print(f"   ✅ 原图: {original_path}")
            
            # 抠图
            transparent_path = RESULT_DIR / f"{name}_transparent.png"
            transparent_pct = remove_green_background(original_path, transparent_path)
            print(f"   ✅ 抠图: {transparent_path} (透明: {transparent_pct:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            if attempt < max_retries - 1:
                continue
            return False
    
    return False

def main():
    """主函数"""
    print("🚀 108好汉批量生成脚本")
    print(f"   总计: {len(HEROES)} 个角色待生成")
    print(f"   速率限制: 每2个角色暂停3分钟")
    print(f"   预计时间: {len(HEROES) * 3 / 2:.0f} 分钟")
    print()
    
    # 检查已有角色
    existing = set()
    for f in OUTPUT_DIR.glob("*.png"):
        existing.add(f.stem)
    
    # 过滤掉已有的
    to_generate = [h for h in HEROES if h["name"] not in existing]
    print(f"   已有: {len(HEROES) - len(to_generate)} 个")
    print(f"   待生成: {len(to_generate)} 个")
    
    success_count = 0
    fail_count = 0
    
    for i, hero in enumerate(to_generate):
        # 生成
        if generate_hero(hero):
            success_count += 1
        else:
            fail_count += 1
        
        # 每2个暂停1分钟（减少等待时间）
        if (i + 1) % 2 == 0 and i < len(to_generate) - 1:
            print(f"\n⏳ 已生成 {i + 1} 个，暂停 1 分钟避免限流...")
            time.sleep(60)
    
    print(f"\n{'='*60}")
    print(f"✅ 完成！成功: {success_count}, 失败: {fail_count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
