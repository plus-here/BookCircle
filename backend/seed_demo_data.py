import os
from datetime import timedelta
from textwrap import dedent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.db import transaction
from django.utils import timezone

from accounts.models import User
from announcements.models import Announcement
from activities.models import Activity, ActivitySignup
from books.models import Book, Chapter, Bookshelf
from clubs.models import Club, ClubSection, ClubMembership, ClubJoinRequest, Post, Comment
from directchat.models import DirectThread, DirectMessage
from groupchat.models import ChatGroup, GroupMember, GroupMessage


PASSWORD = "BookCircle123!"
ADMIN_PASSWORD = "Admin@123456"
NOW = timezone.now()


def dt_days_ago(days: int, hour: int = 20, minute: int = 0):
    base = timezone.localtime(NOW).replace(hour=hour, minute=minute, second=0, microsecond=0)
    return base - timedelta(days=days)


def dt_days_later(days: int, hour: int = 19, minute: int = 0):
    base = timezone.localtime(NOW).replace(hour=hour, minute=minute, second=0, microsecond=0)
    return base + timedelta(days=days)


def stamp(instance, **fields):
    instance.__class__.objects.filter(pk=instance.pk).update(**fields)
    for k, v in fields.items():
        setattr(instance, k, v)
    return instance


USER_SPECS = [
    {
        "username": "admin",
        "email": "admin@bookcircle.local",
        "bio": "BookCircle 站点管理员，负责内容审核、活动发布与演示环境维护。",
        "is_staff": True,
        "is_superuser": True,
        "created_days_ago": 14,
        "password": ADMIN_PASSWORD,
    },
    {
        "username": "linan",
        "email": "linan@bookcircle.local",
        "bio": "偏爱推理和都市小说，习惯边读边记摘抄，也是推理与悬疑社团长。",
        "created_days_ago": 13,
    },
    {
        "username": "zhouqian",
        "email": "zhouqian@bookcircle.local",
        "bio": "科幻探索社管理员，喜欢讨论世界观、技术设定与改编作品。",
        "created_days_ago": 12,
    },
    {
        "username": "wenqi",
        "email": "wenqi@bookcircle.local",
        "bio": "诗歌与散文社成员，常在夜里写阅读手记，也喜欢做活动记录。",
        "created_days_ago": 11,
    },
    {
        "username": "xiaoyu",
        "email": "xiaoyu@bookcircle.local",
        "bio": "校园纪实爱好者，常看非虚构作品，对采访与观察类文本很上头。",
        "created_days_ago": 10,
    },
    {
        "username": "haoran",
        "email": "haoran@bookcircle.local",
        "bio": "新书速递社负责人，每周都会整理新书清单和推荐标签。",
        "created_days_ago": 9,
    },
    {
        "username": "yining",
        "email": "yining@bookcircle.local",
        "bio": "读书会重度参与者，最喜欢在社团里拉大家一起做共读打卡。",
        "created_days_ago": 8,
    },
    {
        "username": "chenmo",
        "email": "chenmo@bookcircle.local",
        "bio": "影视改编讨论社成员，读完书后总要去找改编电影或剧版做比较。",
        "created_days_ago": 7,
    },
    {
        "username": "siyi",
        "email": "siyi@bookcircle.local",
        "bio": "擅长写长评，关注角色塑造和叙事节奏，也常在群里组织讨论。",
        "created_days_ago": 6,
    },
    {
        "username": "peiyao",
        "email": "peiyao@bookcircle.local",
        "bio": "喜欢治愈系和成长题材，书架里永远会留一本到两本慢读作品。",
        "created_days_ago": 5,
    },
    {
        "username": "mingzhe",
        "email": "mingzhe@bookcircle.local",
        "bio": "经常参加活动的活跃用户，偏爱高信息量的讨论与主题分享。",
        "created_days_ago": 4,
    },
    {
        "username": "qiuhe",
        "email": "qiuhe@bookcircle.local",
        "bio": "最近刚加入平台，喜欢跟着社团活动慢慢建立自己的阅读节奏。",
        "created_days_ago": 3,
    },
]


BOOK_SPECS = [
    {
        "title": "凌晨书店",
        "author": "沈知遥",
        "description": "一家只在凌晨开门的旧书店，把一群互不相识的人拉进彼此的人生缝隙中。作品以城市夜色为底色，讨论陪伴、遗憾与重新开始。",
        "chapters": [
            ("雨夜的灯牌", "书店重新亮灯的第一个夜晚"),
            ("借书卡上的名字", "一张旧借书卡牵出十年前的约定"),
            ("读到一半的信", "店里出现了一封从未寄出的信"),
            ("凌晨四点的客人", "每个人都带着无法白天说出口的心事"),
            ("天亮之前", "有人决定留下，有人终于学会告别"),
        ],
    },
    {
        "title": "群星借阅处",
        "author": "林应川",
        "description": "一所大学图书馆地下层的实验阅览室，保存着关于未来城市的试读手稿。故事以轻科幻笔法展开，兼顾校园感与群像关系。",
        "chapters": [
            ("地下层的门禁", "主角第一次进入只对少数人开放的阅览室"),
            ("第七排星图", "一份星图让大家意识到手稿并非虚构"),
            ("模拟城市夜航", "阅读内容与现实课程开始发生奇妙重叠"),
            ("被删去的结尾", "大家尝试拼回一本残缺手稿的结尾"),
            ("光落在书脊上", "关于未来的选择最终回到当下的人身上"),
        ],
    },
    {
        "title": "未寄出的春天",
        "author": "苏遥",
        "description": "一段跨越高三、大学与工作初期的成长书信集，写给朋友、旧日自己与尚未抵达的春天。适合做情绪细腻的阅读展示。",
        "chapters": [
            ("第一封草稿", "在不确定里写下最初的愿望"),
            ("自习室之后", "朋友们在各自岔路口前短暂停住"),
            ("落在四月的站台", "毕业后的重逢并不热闹却很真实"),
            ("把名字写慢一点", "学会重新认识自己与关系"),
            ("春天终于寄出", "那封信没有寄出，但人已经向前走了"),
        ],
    },
    {
        "title": "桥上的风与信",
        "author": "顾知白",
        "description": "偏散文气质的短篇长卷，以一座老桥为地标，把城中不同年龄与职业的人串联起来，适合做文艺型内容展示。",
        "chapters": [
            ("桥东的清晨", "每天最早经过桥的人各自怀着什么"),
            ("信箱旁的老人", "一位老人坚持把纸信投进快被遗忘的铁箱里"),
            ("傍晚风里的人群", "城市节奏与个人感受彼此交错"),
            ("停在桥心", "有人第一次认真看见脚下流过的河"),
            ("回声落下", "风带走了旧消息，也留下了新的答案"),
        ],
    },
    {
        "title": "消失的索引卡",
        "author": "季回",
        "description": "发生在高校图书馆里的轻推理故事，一套被偷换顺序的索引卡引出馆藏背后的旧事与当下的人心。",
        "chapters": [
            ("最后一张空卡", "值班员发现索引柜里少了一张关键卡片"),
            ("误放的目录", "一处细小错位让案件有了方向"),
            ("阅览室证词", "几位读者的叙述互相抵触"),
            ("归档室的脚步声", "夜间巡查时出现了不该有的人"),
            ("索引回到原位", "真相没有想象中惊天，却足够刺痛"),
        ],
    },
    {
        "title": "雨季阅读小组",
        "author": "许禾",
        "description": "四位性格迥异的同学在连绵雨季中成立读书小组，从共读、争论到彼此支持，呈现温柔而真实的校园社群关系。",
        "chapters": [
            ("名单上的第四个人", "本来三人的小组突然多出一位迟到的成员"),
            ("公共课后的楼梯间", "第一次讨论比预想更热烈也更拧巴"),
            ("下雨天的共读表", "大家约定把阅读变成可以看见的日常"),
            ("有人中途沉默", "关系推进时也会遭遇退缩与误解"),
            ("晴天收尾", "小组没有解散，而是变成更自然的陪伴"),
        ],
    },
    {
        "title": "河岸边的旧报纸",
        "author": "周行舟",
        "description": "一本兼具非虚构质感与文学表达的作品，通过旧报纸里的地方新闻，追踪一座小城几十年的公共记忆与普通人命运。",
        "chapters": [
            ("被折起的头版", "一则旧闻成为追索一切的起点"),
            ("码头、市场与学校", "城市的日常版图在采访中慢慢清晰"),
            ("记者没有写完", "一些资料停在最关键的一页"),
            ("河水改道以后", "环境变化改变了职业也改变了关系"),
            ("把新闻读成人", "真正重要的是被报道过的人后来怎样了"),
        ],
    },
    {
        "title": "山谷回声计划",
        "author": "唐微澜",
        "description": "近未来题材作品。研究团队在山谷中测试‘回声保存计划’，试图记录人类最容易消失的私人声音。故事兼具科技设定与情感线。",
        "chapters": [
            ("计划启动日", "项目组第一次把样本声音放进回声装置"),
            ("无人认领的片段", "系统记录到一段没有来源的语音"),
            ("测试场之外", "研究人员的私人生活开始被项目反照"),
            ("噪声里的名字", "所有人都在寻找那段声音真正的主人"),
            ("回声留下的人", "项目结论之外，更重要的是人如何继续生活"),
        ],
    },
]


CLUB_SPECS = [
    {
        "name": "推理与悬疑社",
        "theme": "推理、悬疑与谜题文本",
        "owner": "linan",
        "admins": ["haoran"],
        "members": ["wenqi", "xiaoyu", "siyi", "qiuhe"],
        "post_topics": [
            "本月共读：《消失的索引卡》开读说明",
            "你最喜欢哪一种“误导性线索”？",
            "第 1 周阅读打卡：请写下你最怀疑的人物",
        ],
    },
    {
        "name": "科幻探索社",
        "theme": "科幻、世界观与技术想象",
        "owner": "zhouqian",
        "admins": ["mingzhe"],
        "members": ["linan", "chenmo", "yining", "peiyao"],
        "post_topics": [
            "《群星借阅处》里最吸引你的设定是什么？",
            "如果你能设计一个未来图书馆，会增加什么功能？",
            "社团周报：下周进行科幻短篇闪电分享",
        ],
    },
    {
        "name": "诗歌与散文社",
        "theme": "诗歌、散文与慢读表达",
        "owner": "wenqi",
        "admins": ["peiyao"],
        "members": ["linan", "yining", "qiuhe", "xiaoyu"],
        "post_topics": [
            "《桥上的风与信》适合怎样的阅读速度？",
            "本周摘抄帖：请贴出一句你想记住的话",
            "社团通知：周五晚进行朗读分享会",
        ],
    },
    {
        "name": "非虚构阅读社",
        "theme": "纪实、采访与公共叙事",
        "owner": "xiaoyu",
        "admins": ["siyi"],
        "members": ["wenqi", "mingzhe", "qiuhe", "chenmo"],
        "post_topics": [
            "如何判断一本非虚构作品的材料可信度？",
            "《河岸边的旧报纸》阅读提纲已更新",
            "分享你最近读过的一篇人物报道",
        ],
    },
    {
        "name": "影视改编讨论社",
        "theme": "原著与影视改编比较",
        "owner": "chenmo",
        "admins": ["zhouqian"],
        "members": ["linan", "haoran", "peiyao", "qiuhe"],
        "post_topics": [
            "当原著节奏和影视节奏冲突时，你站哪边？",
            "本周讨论：改编中最难保留的是什么",
            "社团投票：下一次比较阅读选哪部作品",
        ],
    },
    {
        "name": "新书速递社",
        "theme": "新书情报、荐书与书单整理",
        "owner": "haoran",
        "admins": ["yining"],
        "members": ["zhouqian", "mingzhe", "peiyao", "siyi"],
        "post_topics": [
            "本周新书快讯：站内新增 3 本可共读作品",
            "你更看重书单里的哪一个维度：主题、口碑还是篇幅？",
            "社团公告：欢迎补充你想看的新书方向",
        ],
    },
]


ANNOUNCEMENT_SPECS = [
    {
        "title": "平台演示环境已更新：新增社团、活动与聊天样例",
        "published_days_ago": 12,
        "is_published": True,
        "points": [
            "已补充 8 本图书与 40 个章节示例内容，便于首页、详情页和阅读页演示。",
            "已创建 6 个社团、多个板块帖子与评论，方便展示社群互动功能。",
            "已写入群聊与私聊历史消息，进入聊天页即可看到完整示例。",
        ],
    },
    {
        "title": "本周活动预告：夜读接力、共读讨论与改编主题沙龙",
        "published_days_ago": 10,
        "is_published": True,
        "points": [
            "夜读接力活动将采用线上签到 + 线下分享形式。",
            "共读讨论优先面向目标社团开放报名。",
            "活动页已支持查看时间、地点、报名截止时间与已报名记录。",
        ],
    },
    {
        "title": "社团申请流程说明（演示版）",
        "published_days_ago": 9,
        "is_published": True,
        "points": [
            "普通用户可在社团详情页提交申请理由。",
            "团长/管理员可在申请列表中执行通过或驳回。",
            "已预置多条待审批申请，便于你在答辩时直接演示审核流程。",
        ],
    },
    {
        "title": "内容上传规范：公告富文本支持图片、列表与段落",
        "published_days_ago": 7,
        "is_published": True,
        "points": [
            "公告详情页会对富文本进行安全渲染。",
            "建议控制标题长度，正文分段清晰，便于展示。",
            "示例数据已加入 HTML 段落与列表，答辩展示效果更完整。",
        ],
    },
    {
        "title": "管理员仪表盘说明：近 14 日趋势数据已补齐",
        "published_days_ago": 5,
        "is_published": True,
        "points": [
            "用户新增趋势、书架加入趋势、公告发布趋势均已写入样例数据。",
            "管理员登录后可直观看到折线/柱状图不再为空。",
            "后续可继续按同样方式扩充数据，保持统计面板稳定可演示。",
        ],
    },
    {
        "title": "读书打卡周即将开始，请提前完善个人资料",
        "published_days_ago": 3,
        "is_published": True,
        "points": [
            "建议上传头像、填写个人简介，方便社团成员互相识别。",
            "书架阅读进度会作为活动展示的一部分。",
            "演示账号已预置部分阅读记录，你也可以继续追加。",
        ],
    },
    {
        "title": "公告草稿：后续计划加入图书封面批量上传",
        "published_days_ago": 1,
        "is_published": False,
        "points": [
            "该公告为后台草稿，仅用于展示草稿与发布状态差异。",
            "未来计划支持封面批量上传与书籍标签管理。",
        ],
    },
    {
        "title": "公告草稿：准备补充排行榜与热门讨论区",
        "published_days_ago": 0,
        "is_published": False,
        "points": [
            "该草稿用于管理端演示编辑、保存、发布流程。",
            "拟新增热门社团、热门帖子、热门书籍等聚合视图。",
        ],
    },
]


ACTIVITY_SPECS = [
    {
        "title": "夜读接力 · 72 小时阅读挑战",
        "clubs": ["新书速递社", "诗歌与散文社"],
        "days_later": 2,
        "duration_hours": 2,
        "location": "图书馆二楼共享区",
        "status": "published",
        "description": "面向偏慢读与打卡用户的活动。现场会设置签到板、金句墙和自由交流时段。",
        "signup_users": ["linan", "wenqi", "yining", "peiyao"],
    },
    {
        "title": "推理共读会：从线索设计到真相揭示",
        "clubs": ["推理与悬疑社"],
        "days_later": 4,
        "duration_hours": 2,
        "location": "A305 讨论教室",
        "status": "published",
        "description": "围绕《消失的索引卡》展开，重点讨论误导线索、叙述顺序和读者预期。",
        "signup_users": ["linan", "xiaoyu", "siyi"],
    },
    {
        "title": "科幻短篇闪电分享",
        "clubs": ["科幻探索社"],
        "days_later": 5,
        "duration_hours": 1,
        "location": "线上腾讯会议",
        "status": "published",
        "description": "每位成员 5 分钟，用一段设定或一个问题介绍自己最近读到的科幻短篇。",
        "signup_users": ["zhouqian", "linan", "chenmo", "mingzhe"],
    },
    {
        "title": "非虚构写作观察课",
        "clubs": ["非虚构阅读社"],
        "days_later": 7,
        "duration_hours": 2,
        "location": "传媒楼 204",
        "status": "published",
        "description": "结合《河岸边的旧报纸》，讨论如何从地方材料进入公共议题。",
        "signup_users": ["xiaoyu", "mingzhe", "qiuhe"],
    },
    {
        "title": "原著 vs 改编：情节删改讨论沙龙",
        "clubs": ["影视改编讨论社"],
        "days_later": 8,
        "duration_hours": 2,
        "location": "综合楼 B101",
        "status": "published",
        "description": "通过分组讨论比较人物弧光、节奏压缩与媒介表达差异。",
        "signup_users": ["chenmo", "haoran", "peiyao"],
    },
    {
        "title": "社团联合书单共创工作坊",
        "clubs": ["新书速递社", "科幻探索社", "推理与悬疑社"],
        "days_later": 10,
        "duration_hours": 3,
        "location": "信息楼创客空间",
        "status": "published",
        "description": "联合制作站内推荐书单，活动结束后会把成果发布到公告与社团板块。",
        "signup_users": ["linan", "zhouqian", "haoran", "siyi", "mingzhe"],
    },
    {
        "title": "四月主题活动策划会（后台草稿）",
        "clubs": ["新书速递社", "诗歌与散文社"],
        "days_later": 12,
        "duration_hours": 1,
        "location": "行政楼小会议室",
        "status": "draft",
        "description": "草稿活动，用于管理端演示未发布活动的编辑流程。",
        "signup_users": [],
    },
    {
        "title": "已取消活动示例：雨天户外城市观察",
        "clubs": ["非虚构阅读社"],
        "days_later": 6,
        "duration_hours": 2,
        "location": "校外老街",
        "status": "cancelled",
        "description": "取消状态示例，用于展示活动状态切换与列表筛选。",
        "signup_users": [],
    },
]


GROUP_SPECS = [
    {
        "name": "站内新书讨论群",
        "description": "推荐新书、交流书单、同步站内内容更新。",
        "creator": "haoran",
        "members": ["linan", "zhouqian", "wenqi", "haoran", "yining"],
        "messages": [
            ("haoran", "我把这周适合展示的新书都整理进书单了，等会儿发到社团里。"),
            ("linan", "我建议先把《消失的索引卡》放首页，推理社那边讨论度挺高。"),
            ("wenqi", "诗歌与散文社也想推一本到首页，我晚点补一段推荐词。"),
            ("zhouqian", "科幻区这次可以放《群星借阅处》，题材和站点气质很搭。"),
            ("yining", "那我负责把大家的推荐整成统一格式，活动页也同步一下。"),
        ],
    },
    {
        "name": "推理社群聊",
        "description": "围绕推理共读、线索分析和打卡活动展开。",
        "creator": "linan",
        "members": ["linan", "xiaoyu", "siyi", "qiuhe", "haoran"],
        "messages": [
            ("linan", "本周先读到第二章，重点看目录错位和人物不在场证明。"),
            ("xiaoyu", "我已经开始怀疑管理员了，但感觉作者在故意误导。"),
            ("siyi", "我更在意证词之间的时间差，那个细节不像随手写的。"),
            ("qiuhe", "第一次参加共读，有没有不剧透的做笔记方法？"),
            ("haoran", "可以先记“疑点”和“解释”，最后再看哪些能闭合。"),
        ],
    },
    {
        "name": "科幻灵感交换站",
        "description": "分享设定、问题意识和未来城市想象。",
        "creator": "zhouqian",
        "members": ["zhouqian", "chenmo", "linan", "mingzhe", "peiyao"],
        "messages": [
            ("zhouqian", "如果未来图书馆能根据情绪推荐书，你会觉得方便还是可怕？"),
            ("chenmo", "如果算法懂我太多，我可能会更想找一间完全安静的书店。"),
            ("linan", "我接受推荐，但希望还能保留“偶然翻到一本书”的空间。"),
            ("mingzhe", "这个问题很适合拿去做活动讨论，我记一下。"),
            ("peiyao", "说不定“偶然”本身就是最难被技术模拟的体验。"),
        ],
    },
    {
        "name": "活动执行小组",
        "description": "活动前的物料、签到、流程和复盘安排。",
        "creator": "admin",
        "members": ["admin", "haoran", "yining", "mingzhe", "wenqi"],
        "messages": [
            ("admin", "请大家确认周六活动的签到表、投影和现场拍照安排。"),
            ("haoran", "新书展示架我来准备，物料清单已经发群文件。"),
            ("yining", "我负责签到和现场引导，顺便做一次简短的用户采访。"),
            ("mingzhe", "讨论环节我来控时，尽量让每个社团都能发言。"),
            ("wenqi", "我会准备一页朗读分享提示，方便现场暖场。"),
        ],
    },
]


DM_SPECS = [
    {
        "users": ("linan", "zhouqian"),
        "messages": [
            ("linan", "你们科幻社下周活动想不想和新书速递社联动一下？"),
            ("zhouqian", "可以，我正想做一个“未来图书馆”方向的快闪分享。"),
            ("linan", "那我把场地信息整理给你，顺便把报名帖挂到群里。"),
            ("zhouqian", "好，我今晚先写一版活动介绍。"),
        ],
    },
    {
        "users": ("wenqi", "peiyao"),
        "messages": [
            ("wenqi", "朗读分享会你愿意做开场吗？我觉得你的节奏很适合。"),
            ("peiyao", "可以呀，但我想先选一段不太长的文字。"),
            ("wenqi", "那就从《桥上的风与信》第三章挑吧，气氛很好。"),
            ("peiyao", "好，我今晚再读一遍，明天把段落发给你。"),
        ],
    },
    {
        "users": ("xiaoyu", "mingzhe"),
        "messages": [
            ("xiaoyu", "非虚构观察课我准备把采访提纲做成表单，你觉得合适吗？"),
            ("mingzhe", "很合适，活动现场收回来的内容也方便后面复盘。"),
            ("xiaoyu", "那我再加一项“最打动你的细节”，这样更适合后续展示。"),
            ("mingzhe", "可以，到时候我帮你一起整理成公告素材。"),
        ],
    },
    {
        "users": ("chenmo", "haoran"),
        "messages": [
            ("chenmo", "原著和改编的投票我看了，大家都挺想聊节奏压缩。"),
            ("haoran", "对，我准备把问题拆成三块：删改、人物和结尾。"),
            ("chenmo", "那我再补两个例子，现场更容易带起来。"),
            ("haoran", "行，我们周三前把提纲敲定。"),
        ],
    },
]


def create_or_update_user(spec):
    password = spec.get("password", PASSWORD)
    user, _ = User.objects.get_or_create(
        username=spec["username"],
        defaults={
            "email": spec["email"],
            "bio": spec["bio"],
            "is_staff": spec.get("is_staff", False),
            "is_superuser": spec.get("is_superuser", False),
            "is_active": True,
        },
    )
    user.email = spec["email"]
    user.bio = spec["bio"]
    user.is_staff = spec.get("is_staff", False)
    user.is_superuser = spec.get("is_superuser", False)
    user.is_active = True
    user.set_password(password)
    user.save()
    stamp(user, created_at=dt_days_ago(spec["created_days_ago"], 9, 30), updated_at=dt_days_ago(max(spec["created_days_ago"] - 1, 0), 20, 0))
    return user


def make_chapter_content(book_title, chapter_title, focus):
    return dedent(
        f"""
        【章节导读】
        《{book_title}》这一章围绕“{focus}”展开。人物表面上只是做了一件很普通的事，但真正推动故事的，是他们没有说出口的情绪与判断。

        故事从一个很小的动作开始：有人停下脚步，有人把话说到一半，有人突然意识到自己一直回避的问题已经无法继续回避。正因为开场克制，读者才会更快进入文本内部的节奏。

        在这一章里，空间并不是单纯的背景。灯光、楼道、雨声、窗边的风、桌面上被翻开的纸页，都在无声地提示人物关系的变化。它们让文本既有画面感，也保留了适合讨论的留白。

        如果把整部作品看成一次缓慢推进的阅读旅程，那么“{chapter_title}”就像其中最关键的一次转弯。人物开始重新理解彼此，也开始重新理解自己先前做出的选择。

        阅读提示：可以留意本章里反复出现的意象、沉默后的回答，以及那些看似轻描淡写却会在后文继续发酵的细节。这些元素都很适合在社团帖子、共读活动和课堂展示里继续展开。
        """
    ).strip()


def make_post_content(club_name, theme, topic):
    return dedent(
        f"""
        这是一篇来自【{club_name}】的主题帖，讨论方向聚焦在：{topic}。

        社团当前的阅读氛围比较稳定，大家既希望有明确的问题切入，也希望保留自由表达空间。因此本帖会优先鼓励成员从自己的阅读体验出发，再慢慢过渡到对文本结构、人物与主题的分析。

        你可以从以下几个角度展开：
        1. 这次阅读中最先抓住你的细节是什么？
        2. {theme} 这一方向在作品里是如何被具体呈现的？
        3. 如果把这次讨论延伸成一次线下活动，你最想让大家重点聊什么？

        欢迎大家在评论区写下长评、短感受或打卡笔记。这个帖子也会作为后续社团活动和展示页面的素材来源。
        """
    ).strip()


def make_comment(author_name, angle):
    return f"我是从“{angle}”这个角度进入文本的，越读越觉得细节安排很克制，但后劲非常足，适合继续展开讨论。"


def announcement_html(title, points):
    bullets = "".join(f"<li>{p}</li>" for p in points)
    return dedent(
        f"""
        <p><strong>{title}</strong></p>
        <p>为便于系统演示与答辩展示，当前站点已经补充一批可直接展示的示例内容。你可以在用户端、管理端与聊天模块中看到完整数据链路。</p>
        <ul>{bullets}</ul>
        <p>如需继续扩充，可沿用相同结构追加图书、帖子、评论、公告和活动。示例数据均为原创演示文本，适合教学与毕设展示场景。</p>
        """
    ).strip()


@transaction.atomic
def main():
    users = {spec["username"]: create_or_update_user(spec) for spec in USER_SPECS}

    books = {}
    chapters = {}
    for idx, spec in enumerate(BOOK_SPECS, start=1):
        book, _ = Book.objects.update_or_create(
            title=spec["title"],
            defaults={
                "author": spec["author"],
                "description": spec["description"],
                "is_published": True,
            },
        )
        stamp(book, created_at=dt_days_ago(15 - idx, 10, 0), updated_at=dt_days_ago(max(13 - idx, 0), 18, 0))
        books[spec["title"]] = book
        chapters[spec["title"]] = []

        for order, (chapter_title, focus) in enumerate(spec["chapters"], start=1):
            chapter, _ = Chapter.objects.update_or_create(
                book=book,
                order=order,
                defaults={
                    "title": chapter_title,
                    "content": make_chapter_content(spec["title"], chapter_title, focus),
                },
            )
            stamp(chapter, created_at=dt_days_ago(15 - idx, 11 + min(order, 5), 0), updated_at=dt_days_ago(max(12 - idx, 0), 19, 0))
            chapters[spec["title"]].append(chapter)

    clubs = {}
    club_sections = {}
    for idx, spec in enumerate(CLUB_SPECS, start=1):
        club, _ = Club.objects.update_or_create(
            name=spec["name"],
            defaults={
                "description": f"围绕 {spec['theme']} 组织共读、讨论与线下活动，适合持续输出站内帖子与活动记录。",
                "owner": users[spec["owner"]],
            },
        )
        if club.owner_id != users[spec["owner"]].id:
            club.owner = users[spec["owner"]]
            club.save()
        stamp(club, created_at=dt_days_ago(16 - idx, 14, 0), updated_at=dt_days_ago(max(10 - idx, 0), 20, 0))
        clubs[spec["name"]] = club

        club_sections[spec["name"]] = {}
        for sec_idx, sec_name in enumerate(["社团公告", "主题讨论", "打卡分享"], start=1):
            section, _ = ClubSection.objects.update_or_create(
                club=club,
                name=sec_name,
                defaults={"order": sec_idx},
            )
            club_sections[spec["name"]][sec_name] = section

        ClubMembership.objects.update_or_create(club=club, user=users[spec["owner"]], defaults={"role": "owner"})
        for admin_name in spec["admins"]:
            ClubMembership.objects.update_or_create(club=club, user=users[admin_name], defaults={"role": "admin"})
        for member_name in spec["members"]:
            ClubMembership.objects.update_or_create(club=club, user=users[member_name], defaults={"role": "member"})

        topics = spec["post_topics"]
        section_order = ["社团公告", "主题讨论", "打卡分享"]
        authors = [spec["owner"], *(spec["admins"][:1] or [spec["owner"]]), spec["members"][0]]
        for post_idx, topic in enumerate(topics):
            section_name = section_order[post_idx % len(section_order)]
            author_name = authors[post_idx % len(authors)]
            post, _ = Post.objects.update_or_create(
                club=club,
                section=club_sections[spec["name"]][section_name],
                author=users[author_name],
                title=topic,
                defaults={
                    "content": make_post_content(spec["name"], spec["theme"], topic),
                    "is_pinned": section_name == "社团公告",
                },
            )
            stamp(post, created_at=dt_days_ago(12 - post_idx, 21, 0), updated_at=dt_days_ago(max(9 - post_idx, 0), 22, 0))

            comment_authors = [n for n in [*spec["members"], *spec["admins"]] if n != author_name][:2]
            for c_idx, commenter in enumerate(comment_authors, start=1):
                comment, _ = Comment.objects.get_or_create(
                    post=post,
                    author=users[commenter],
                    content=make_comment(commenter, f"第 {c_idx} 个评论角度"),
                )
                stamp(comment, created_at=dt_days_ago(11 - post_idx, 22, 10 * c_idx))

    pending_requests = [
        ("推理与悬疑社", "peiyao", "最近开始集中读推理作品，想跟着社团一起做共读记录。"),
        ("科幻探索社", "qiuhe", "想参加未来图书馆主题讨论，也希望认识更多同好。"),
        ("影视改编讨论社", "xiaoyu", "最近在做原著与改编比较，想参与相关活动。"),
        ("非虚构阅读社", "linan", "想补足非虚构阅读视角，也想参与观察课。"),
    ]
    for idx, (club_name, user_name, reason) in enumerate(pending_requests, start=1):
        club = clubs[club_name]
        if not ClubMembership.objects.filter(club=club, user=users[user_name]).exists():
            jr, _ = ClubJoinRequest.objects.update_or_create(
                club=club,
                user=users[user_name],
                defaults={"status": "pending", "reason": reason, "reviewed_at": None, "reviewed_by": None},
            )
            stamp(jr, created_at=dt_days_ago(4 + idx, 15, 0))

    announcements = []
    for idx, spec in enumerate(ANNOUNCEMENT_SPECS, start=1):
        published_at = dt_days_ago(spec["published_days_ago"], 9 + idx % 4, 0) if spec["is_published"] else None
        announcement, _ = Announcement.objects.update_or_create(
            title=spec["title"],
            defaults={
                "content": announcement_html(spec["title"], spec["points"]),
                "is_published": spec["is_published"],
                "published_at": published_at,
                "created_by": users["admin"],
            },
        )
        created_at = dt_days_ago(max(spec["published_days_ago"] + 1, 0), 18, 0)
        stamp(announcement, created_at=created_at, updated_at=created_at + timedelta(hours=2), published_at=published_at)
        announcements.append(announcement)

    activity_map = {}
    for idx, spec in enumerate(ACTIVITY_SPECS, start=1):
        start_time = dt_days_later(spec["days_later"], 19, 0)
        end_time = start_time + timedelta(hours=spec["duration_hours"])
        deadline = start_time - timedelta(days=1)
        activity, _ = Activity.objects.update_or_create(
            title=spec["title"],
            defaults={
                "description": spec["description"],
                "location": spec["location"],
                "start_time": start_time,
                "end_time": end_time,
                "signup_deadline": deadline,
                "status": spec["status"],
                "created_by": users["admin"],
            },
        )
        activity.targets.set([clubs[name] for name in spec["clubs"]])
        stamp(activity, created_at=dt_days_ago(10 - min(idx, 9), 16, 0), updated_at=dt_days_ago(max(8 - min(idx, 8), 0), 19, 0))
        activity_map[spec["title"]] = activity

        for user_name in spec["signup_users"]:
            memberships = ClubMembership.objects.filter(user=users[user_name], club__in=activity.targets.all()).select_related("club")
            membership = memberships.first()
            if membership:
                signup, _ = ActivitySignup.objects.update_or_create(
                    activity=activity,
                    user=users[user_name],
                    defaults={"club": membership.club, "status": "signed"},
                )
                stamp(signup, created_at=dt_days_ago(7 - idx if idx < 7 else 1, 12, 0))

    book_list = list(books.values())
    user_list = [u for name, u in users.items() if name != "admin"]
    for idx, user in enumerate(user_list):
        for offset in range(2):
            book = book_list[(idx + offset) % len(book_list)]
            chapter_list = chapters[book.title]
            chapter = chapter_list[min((idx + offset) % len(chapter_list), len(chapter_list) - 1)]
            shelf, _ = Bookshelf.objects.get_or_create(user=user, book=book)
            shelf.last_read_chapter = chapter
            shelf.last_read_at = dt_days_ago((idx + offset) % 14, 21, 30)
            shelf.save(update_fields=["last_read_chapter", "last_read_at"])
            stamp(shelf, added_at=dt_days_ago((idx * 2 + offset) % 14, 20, 0))

    groups = {}
    for idx, spec in enumerate(GROUP_SPECS, start=1):
        group, _ = ChatGroup.objects.update_or_create(
            name=spec["name"],
            defaults={
                "description": spec["description"],
                "creator": users[spec["creator"]],
                "is_public": True,
            },
        )
        stamp(group, created_at=dt_days_ago(9 - idx, 18, 0), updated_at=dt_days_ago(2, 18, 0))
        groups[spec["name"]] = group

        for member_name in spec["members"]:
            role = "owner" if member_name == spec["creator"] else "member"
            GroupMember.objects.update_or_create(group=group, user=users[member_name], defaults={"role": role})

        for msg_idx, (sender_name, content) in enumerate(spec["messages"], start=1):
            msg, _ = GroupMessage.objects.get_or_create(group=group, sender=users[sender_name], content=content)
            stamp(msg, created_at=dt_days_ago(max(5 - idx, 0), 19, 5 * msg_idx))

    for idx, spec in enumerate(DM_SPECS, start=1):
        a = users[spec["users"][0]]
        b = users[spec["users"][1]]
        u1, u2 = DirectThread.normalize_pair(a.id, b.id)
        thread, _ = DirectThread.objects.get_or_create(user1_id=u1, user2_id=u2)
        stamp(thread, created_at=dt_days_ago(8 - idx, 17, 0))
        for m_idx, (sender_name, content) in enumerate(spec["messages"], start=1):
            msg, _ = DirectMessage.objects.get_or_create(thread=thread, sender=users[sender_name], content=content)
            stamp(msg, created_at=dt_days_ago(8 - idx, 17, 5 * m_idx))

    print("\n=== BookCircle 演示数据已写入 ===")
    print(f"用户数: {User.objects.count()}")
    print(f"书籍数: {Book.objects.count()} / 章节数: {Chapter.objects.count()}")
    print(f"社团数: {Club.objects.count()} / 帖子数: {Post.objects.count()} / 评论数: {Comment.objects.count()}")
    print(f"公告数: {Announcement.objects.count()} / 活动数: {Activity.objects.count()}")
    print(f"群聊数: {ChatGroup.objects.count()} / 私聊线程数: {DirectThread.objects.count()}")
    print("\n管理员账号: admin / Admin@123456")
    print("推荐演示账号: linan / BookCircle123!")
    print("其他示例账号密码统一: BookCircle123!")
    print(", ".join([u["username"] for u in USER_SPECS if u["username"] != "admin"]))


if __name__ == "__main__":
    main()
