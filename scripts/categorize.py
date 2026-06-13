#!/usr/bin/env python3
"""给 unnamed/other 类股票按名字和已知业务分类"""
import json, os

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

# 根据名字/代码快速分类（AI 相关领域）
# compute: AI算力/服务器/数据中心
# optical: 光通信/光模块/光纤
# chip: 芯片/半导体/封测/设备
# robot: 机器人/自动化
# app: AI软件/应用/算法
# infra: 云/网络/安全/基础设施
# other: 难以归类

CATEGORY_RULES = {
    "compute": [
        "浪潮", "曙光", "服务器", "算力", "鸿博", "莲花健康", "恒为", "拓维",
        "工业富联", "协创数据", "中兴通讯", "神州数码", "威星智能",
        "数据港", "光环新网", "首都在线", "优刻得", "青云",
        "网宿", "证通电子", "依米康",
    ],
    "optical": [
        "光", "旭创", "易盛", "天孚", "新易盛", "德科立", "源杰",
        "仕佳", "腾景", "华工", "联特", "太辰光", "博创",
        "光迅", "长飞", "亨通", "中天", "华脉", "通鼎", "烽火",
        "剑桥", "铭普", "光库", "富信", "永鼎", "特发",
    ],
    "chip": [
        "芯片", "半导体", "海光", "寒武纪", "龙芯", "景嘉微", "紫光国微",
        "韦尔", "兆易", "北京君正", "芯原", "澜起", "华天",
        "通富", "长电", "北方华创", "中微", "华海清科", "拓荆",
        "华大九天", "广立微", "概伦", "国芯", "恒烁", "芯朋",
        "圣邦", "斯达", "晶丰", "乐鑫", "瑞芯微", "全志",
        "佰维", "兆易创新", "中芯国际", "紫光", "翱捷",
        "杰华特", "富瀚微", "纳芯微", "思瑞浦", "卓胜微",
        "格科微", "唯捷创芯", "炬芯", "力芯微", "南芯",
        "帝奥微", "灿瑞", "必易微", "英集芯", "芯导",
        "敏芯", "臻镭", "铖昌", "振华风光", "电科芯片",
        "太极实业", "康强", "兴森", "生益", "宏昌",
    ],
    "robot": [
        "机器人", "谐波", "减速器", "绿的", "埃斯顿", "埃夫特",
        "新时达", "拓斯达", "机器人", "汇川", "步科", "禾川",
        "雷赛", "信捷", "正弦", "伟创", "鸣志",
        "科德数控", "华中数控",
    ],
    "app": [
        "三六零", "科大讯飞", "同花顺", "海康威视", "大华",
        "金山办公", "万兴", "虹软", "格灵", "云从", "商汤",
        "云知声", "思必驰", "依图", "第四范式",
        "深信服", "启明星辰", "绿盟", "天融信", "奇安信",
        "美亚柏科", "安恒", "山石", "迪普", "数字认证",
        "东方通", "宝兰德", "普元",
        "东软", "中软", "太极", "浪潮软件", "万达信息",
        "用友", "金蝶", "广联达", "石基", "鼎捷",
        "恒生电子", "赢时胜", "金证", "顶点",
        "四维图新", "超图", "中科星图", "航天宏图",
        "科大智能", "熵基", "汉王", "川大智胜", "格灵深瞳",
        "千方", "银江", "易华录", "辰安",
        "拓尔思", "彩讯", "梦网", "二六三", "会畅",
        "神州泰岳", "天源迪科", "博彦", "中科金财",
        "赛意", "法本", "慧博云通", "润和", "诚迈",
        "中科创达", "光庭", "经纬恒润",
    ],
    "infra": [
        "数据港", "光环新网", "宝信", "奥飞", "万国",
        "世纪互联", "鹏博士", "网宿", "首都在线",
        "中国移动", "中国电信", "中国联通",
        "紫光股份", "星网锐捷", "共进", "锐捷",
        "烽火通信", "中兴通讯", "新华三",
        "中科曙光", "浪潮信息", "联想",
        "英维克", "高澜", "申菱", "依米康", "佳力图",
        "沪电", "深南电路", "胜宏", "景旺", "生益",
        "顺丰控股", "鼎通", "奕东",
        "科华数据", "科士达", "易事特", "中恒电气",
    ],
}

def classify(name, code):
    name = name or ''
    for cat, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in name:
                return cat
    return "other"

def main():
    with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Also remove unnamed placeholder stocks
    data['stocks'] = [s for s in data['stocks'] if s['name'] != s['code'] and s['name'] != '']

    # Classify stocks currently in "other" category
    reclassified = 0
    for stock in data['stocks']:
        if stock['category'] == 'other':
            new_cat = classify(stock['name'], stock['code'])
            if new_cat != 'other':
                stock['category'] = new_cat
                reclassified += 1

    data['total'] = len(data['stocks'])
    data['updated'] = "2026-06-13T18:30:00+08:00"

    with open(UNIVERSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    from collections import Counter
    cats = Counter(s['category'] for s in data['stocks'])
    print(f"Reclassified: {reclassified}")
    print(f"Total: {data['total']}")
    print(f"Categories: {dict(cats)}")

if __name__ == '__main__':
    main()
