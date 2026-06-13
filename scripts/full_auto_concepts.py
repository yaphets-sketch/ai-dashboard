#!/usr/bin/env python3
"""
全量概念自动推断：基于股票名称+核心业务关键词，批量生成概念标签
不需要调用 MCP，纯本地知识库推理
"""
import json, os

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

# 已手动校验的股票
MANUAL = {
    "300308": {"CPO概念":True,"光通信模块":True,"算力概念":True,"F5G概念":True,"5G概念":True,"无人驾驶":False},
    "300502": {"CPO概念":True,"光通信模块":True,"算力概念":True,"英伟达概念":True},
    "300394": {"CPO概念":True,"光通信模块":True,"算力概念":True,"英伟达概念":True},
    "688498": {"CPO概念":True,"光通信模块":True,"国产芯片":True},
    "688313": {"CPO概念":True,"光通信模块":True,"国产芯片":True,"光纤概念":False},
    "688205": {"CPO概念":True,"光通信模块":True,"国产芯片":True},
    "688048": {"CPO概念":True,"光通信模块":True,"国产芯片":True},
    "688195": {"CPO概念":True,"光通信模块":True},
    "002281": {"CPO概念":True,"光通信模块":True,"F5G概念":True,"5G概念":True,"量子科技":None,"国产芯片":None},
    "601869": {"光纤概念":True,"CPO概念":None,"算力概念":None},
    "600487": {"光纤概念":True,"CPO概念":None,"算力概念":None},
    "600522": {"光纤概念":True,"CPO概念":None,"算力概念":None},
    "688256": {"国产芯片":True,"AI芯片":True,"算力概念":True,"汽车芯片":None},
    "688041": {"国产芯片":True,"AI芯片":True,"算力概念":True},
    "688981": {"国产芯片":True,"中芯国际概念":True,"国家大基金持股":True,"先进封装":None},
    "002371": {"国产芯片":True,"中芯国际概念":True,"国家大基金持股":True},
    "600584": {"国产芯片":True,"先进封装":True,"国家大基金持股":True,"存储芯片":None},
    "002156": {"国产芯片":True,"先进封装":True,"CPO概念":False,"存储芯片":None,"AI PC":None},
    "688525": {"存储芯片":True,"国产芯片":True,"AI PC":None,"AI手机":None,"AI眼镜":None,"机器人概念":False,"先进封装":None},
    "603986": {"存储芯片":True,"国产芯片":True,"MCU芯片":True,"人工智能":None,"AI眼镜":None,"汽车芯片":None},
    "688008": {"国产芯片":True,"存储芯片":True,"算力概念":None},
    "688012": {"国产芯片":True,"中芯国际概念":True,"国家大基金持股":True},
    "603019": {"算力概念":True,"国产芯片":None,"人工智能":None},
    "000977": {"算力概念":True,"人工智能":True},
    "601138": {"算力概念":True,"人工智能":True,"液冷服务器":True,"英伟达概念":True,"机器人概念":None,"CPO概念":False,"消费电子概念":True},
    "002230": {"人工智能":True,"AI应用":True,"多模态AI":True,"AI智能体":True},
    "688017": {"机器人概念":True,"人形机器人":True,"减速器":True,"专精特新":True,"半导体概念":False},
    "002463": {"PCB概念":True,"算力概念":True},
    "002916": {"PCB概念":True,"国产芯片":True},
    "002938": {"PCB概念":True,"消费电子概念":True},
    "600183": {"PCB概念":True,"国产芯片":None},
    "688629": {"铜缆高速连接":True,"算力概念":True,"CPO概念":None},
    "600330": {"国产芯片":None,"机器人概念":None},
    "600667": {"国产芯片":True,"存储芯片":None},
    "603678": {"国产芯片":True,"5G概念":None},
    "688120": {"国产芯片":True,"中芯国际概念":True},
    "688143": {"光纤概念":True,"光通信模块":None},
    "688170": {"国产芯片":True,"中芯国际概念":True},
    "688220": {"国产芯片":True,"5G概念":True,"物联网":True},
    "688766": {"国产芯片":True,"存储芯片":True},
    "688047": {"国产芯片":True,"算力概念":None},
    "002384": {"PCB概念":True,"消费电子概念":True,"国产芯片":None},
    "603760": {"国产芯片":True},
    "002119": {"国产芯片":True},
    "002185": {"国产芯片":True,"先进封装":True},
    "000021": {"国产芯片":None,"消费电子概念":True},
    "000725": {"消费电子概念":True,"物联网":True,"人工智能":None},
    "000988": {"CPO概念":True,"光通信模块":True,"算力概念":True,"5G概念":True,"F5G概念":True,"激光雷达":None},
}

# 按名称关键词自动推断
NAME_CONCEPTS = {
    "光电": [("光学光电子",True),("CPO概念",None),("光通信模块",None)],
    "光": [("光通信模块",None)],
    "芯": [("国产芯片",True)],
    "微": [("国产芯片",True)],
    "存储": [("存储芯片",True)],
    "半导": [("国产芯片",True)],
    "晶": [("国产芯片",True)],
    "通信": [("5G概念",True),("通信设备",True)],
    "智能": [("人工智能",None),("机器人概念",None)],
    "机器": [("机器人概念",True)],
    "数据": [("数据要素",None),("数据中心",None)],
    "云": [("云计算",True)],
    "软件": [("AI应用",None),("信创",None)],
    "网络": [("网络安全",None),("物联网",None)],
    "安全": [("数据安全",True)],
    "信息": [("信创",None),("人工智能",None)],
    "科技": [("国产芯片",None),("人工智能",None)],
    "电子": [("消费电子概念",None)],
    "传感": [("传感器",True)],
    "激光": [("激光雷达",True),("光通信模块",None)],
    "自动": [("机器人概念",None),("机器视觉",None)],
    "精密": [("机器人概念",None),("消费电子概念",None)],
    "材料": [("国产芯片",None)],
    "新材": [("国产芯片",None)],
    "设备": [("国产芯片",None)],
    "仪器": [("国产芯片",None)],
    "互联": [("工业互联网",True)],
}

def auto_infer(stock):
    """根据名称+业务推断概念标签"""
    code = stock["code"]
    name = stock["name"]
    biz = stock.get("core_business", "")
    cat = stock["category"]
    text = name + biz

    concepts = {}

    # 按名称关键词
    for kw, tags in NAME_CONCEPTS.items():
        if kw in name:
            for tag, verified in tags:
                if tag not in concepts:
                    concepts[tag] = verified

    # 按业务关键词
    biz_map = {
        "光模块": [("CPO概念",True),("光通信模块",True),("算力概念",True)],
        "光器件": [("CPO概念",True),("光通信模块",True)],
        "光芯片": [("CPO概念",True),("光通信模块",True),("国产芯片",True)],
        "光纤": [("光纤概念",True),("光通信模块",None)],
        "光缆": [("光纤概念",True),("5G概念",None)],
        "芯片": [("国产芯片",True)],
        "半导体": [("国产芯片",True)],
        "封测": [("先进封装",True),("国产芯片",True)],
        "封装": [("先进封装",True),("国产芯片",None)],
        "PCB": [("PCB概念",True),("算力概念",None)],
        "覆铜板": [("PCB概念",True)],
        "IC载板": [("PCB概念",True),("国产芯片",True)],
        "存储": [("存储芯片",True),("国产芯片",True)],
        "MCU": [("MCU芯片",True),("国产芯片",True)],
        "CPU": [("国产芯片",True),("算力概念",None)],
        "GPU": [("AI芯片",True),("算力概念",True)],
        "算力": [("算力概念",True),("人工智能",True)],
        "服务器": [("算力概念",True),("液冷服务器",None),("人工智能",None)],
        "数据中心": [("数据中心(AIDC)",True),("算力概念",True)],
        "IDC": [("数据中心(AIDC)",True),("算力概念",None)],
        "液冷": [("液冷服务器",True),("算力概念",None)],
        "连接器": [("铜缆高速连接",None),("CPO概念",None)],
        "铜缆": [("铜缆高速连接",True),("算力概念",None)],
        "机器人": [("机器人概念",True)],
        "谐波": [("减速器",True),("机器人概念",True)],
        "减速器": [("减速器",True),("机器人概念",True)],
        "伺服": [("机器人概念",True)],
        "AI": [("人工智能",True)],
        "人工智能": [("人工智能",True)],
        "大模型": [("人工智能",True),("多模态AI",None)],
        "AI应用": [("AI应用",True),("人工智能",True)],
        "软件": [("AI应用",None),("信创",None),("人工智能",None)],
        "SaaS": [("云计算",True),("AI应用",None)],
        "云计算": [("云计算",True),("算力概念",None)],
        "云服务": [("云计算",True),("算力概念",None)],
        "安全": [("数据安全",True),("信创",None)],
        "信创": [("信创",True)],
        "操作系统": [("国产操作系统",True),("信创",True)],
        "物联网": [("物联网",True)],
        "智能家居": [("物联网",True),("人工智能",None)],
        "智慧城市": [("物联网",True),("人工智能",None)],
        "传感器": [("传感器",True),("物联网",None)],
        "MEMS": [("传感器",True),("国产芯片",None)],
        "MLCC": [("国产芯片",None),("消费电子概念",None)],
        "消费电子": [("消费电子概念",True)],
        "手机": [("消费电子概念",True),("AI手机",None)],
        "汽车": [("汽车芯片",None),("无人驾驶",None)],
        "5G": [("5G概念",True)],
        "6G": [("6G概念",True)],
        "自动驾驶": [("无人驾驶",True),("激光雷达",None)],
        "激光": [("激光雷达",True),("光通信模块",None)],
        "雷达": [("激光雷达",True),("无人驾驶",None)],
        "新能源": [("新能源",True)],
        "光伏": [("光伏概念",True)],
        "锂电": [("锂电池概念",True)],
        "电源": [("液冷服务器",None)],
        "检测": [("国产芯片",None)],
        "测试": [("国产芯片",None)],
        "CIS": [("国产芯片",True),("消费电子概念",True)],
        "图像传感": [("传感器",True),("国产芯片",True)],
    }

    for kw, tags in biz_map.items():
        if kw in text:
            for tag, verified in tags:
                if tag not in concepts:
                    concepts[tag] = verified

    # 按分类推断
    if not concepts:
        cat_defaults = {
            "chip": [("国产芯片",True)],
            "optical": [("光通信模块",None)],
            "compute": [("算力概念",None)],
            "robot": [("机器人概念",None)],
            "app": [("人工智能",None),("AI应用",None)],
            "infra": [("数据中心(AIDC)",None)],
        }
        for tag, verified in cat_defaults.get(cat, []):
            if tag not in concepts:
                concepts[tag] = verified

    # Add more keyword rules for other category
    extra_name_map = {
        "四方": [("智能电网",True),("电力物联网",True)],
        "东材": [("绝缘材料",True),("新能源",None)],
        "宏和": [("消费电子概念",None)],
        "天和": [("稀土永磁",True),("新能源",None)],
        "淳中": [("消费电子概念",None),("国产芯片",None)],
        "华虹": [("国产芯片",True),("晶圆代工",True),("中芯国际概念",None)],
        "有研": [("新材料",True),("国产芯片",None)],
        "索辰": [("AI应用",True),("工业软件",True)],
        "南亚": [("PCB概念",True),("覆铜板",True)],
        "盛科": [("国产芯片",True),("通信设备",True),("算力概念",None)],
        "优迅": [("国产芯片",True),("光通信模块",True)],
        "晶合": [("国产芯片",True),("晶圆代工",True)],
        "帝奥": [("国产芯片",True),("消费电子概念",None)],
        "深科技": [("消费电子概念",True),("国产芯片",None)],
        "中钨": [("有色金属",True),("国产芯片",None)],
        "京东方": [("消费电子概念",True),("面板",True),("物联网",True)],
        "华工": [("CPO概念",True),("光通信模块",True),("激光雷达",True),("算力概念",True)],
        "得润": [("消费电子概念",True),("连接器",True)],
        "智微": [("AI PC",True),("消费电子概念",True)],
        "大族": [("激光雷达",True),("机器人概念",None)],
        "协鑫": [("新能源",True),("算力概念",None)],
        "中材": [("新材料",True),("风电",None)],
        "康强": [("国产芯片",True),("引线框架",True)],
        "华天": [("国产芯片",True),("先进封装",True)],
        "天娱": [("AI应用",None),("数字人",None)],
        "中恒": [("电源设备",True),("算力概念",None)],
        "云南锗业": [("有色金属",True),("国产芯片",None)],
        "兴森": [("PCB概念",True),("国产芯片",None)],
        "江海": [("被动元件",True),("新能源",None)],
        "麦格米特": [("电源设备",True),("机器人概念",None)],
        "信维": [("消费电子概念",True),("5G概念",True)],
        "硕贝德": [("消费电子概念",True),("5G概念",None)],
        "菲利华": [("新材料",True),("国产芯片",None)],
        "三环": [("被动元件",True),("消费电子概念",True)],
        "昊志": [("机器人概念",True),("主轴",True)],
        "罗博特科": [("机器人概念",None),("自动化",True)],
        "中富": [("PCB概念",True)],
        "阿尔特": [("无人驾驶",None),("汽车设计",True)],
        "欧陆通": [("电源设备",True),("消费电子概念",None)],
        "科翔": [("PCB概念",True)],
        "春晖": [("智能电网",True)],
        "铜冠": [("有色金属",True)],
        "凡拓": [("AI应用",None),("数字人",None)],
        "鼎泰": [("新材料",True)],
        "国际复材": [("新材料",True)],
        "铜峰": [("被动元件",True)],
    }

    for kw, tags in extra_name_map.items():
        if kw in name:
            for tag, verified in tags:
                if tag not in concepts:
                    concepts[tag] = verified

def main():
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for stock in data["stocks"]:
        code = stock["code"]
        if code in MANUAL:
            stock["concepts"] = [{"name": k, "verified": v, "detail": ""} for k, v in MANUAL[code].items()]
            updated += 1
            continue

        # Auto-infer
        stock["concepts"] = auto_infer(stock)
        if stock["concepts"]:
            updated += 1

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with_c = sum(1 for s in data["stocks"] if s.get("concepts"))
    print(f"Total: {data['total']}")
    print(f"With concepts: {with_c} ({with_c*100//data['total']}%)")
    print(f"Manual: {len(MANUAL)}, Auto-inferred: {with_c - len(MANUAL)}")

if __name__ == "__main__":
    main()
