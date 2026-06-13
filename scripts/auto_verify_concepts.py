#!/usr/bin/env python3
"""
概念自动校验引擎：根据核心业务自动判定 ✅/⚠️/❌
"""
import json, os, re

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

# AI相关概念 → 匹配规则
# (概念名, 正面关键词, 负面关键词/排除条件)
CONCEPT_RULES = [
    # 光通信
    ("CPO概念", ["光模块","光器件","光芯片","光通信","光引擎","硅光"], []),
    ("光通信模块", ["光模块","光器件","光通信","光纤"], []),
    ("光纤概念", ["光纤","光缆","预制棒"], ["光模块"]),
    ("F5G概念", ["光通信","光纤","光模块","5G","通信设备"], []),
    # 芯片
    ("存储芯片", ["存储","NAND","NOR","DRAM","Flash","SSD","内存"], []),
    ("国产芯片", ["芯片","集成电路","半导体","IC"], []),
    ("MCU芯片", ["MCU","微控制器","单片机"], []),
    ("汽车芯片", ["车规","汽车电子","车载芯片","车用"], []),
    ("AI芯片", ["AI芯片","GPU","NPU","DCU","TPU","加速卡","推理芯片"], []),
    ("先进封装", ["封测","封装","SiP","Chiplet","FC-BGA","2.5D","3D封装","Fan-out"], []),
    ("第三代半导体", ["SiC","GaN","碳化硅","氮化镓"], []),
    # AI/算力
    ("算力概念", ["算力","服务器","数据中心","AI计算","高性能计算","智算"], []),
    ("算力租赁", ["算力租赁","算力出租","GPU租赁"], []),
    ("人工智能", ["AI","人工智能","大模型","机器学习","深度学习","NLP","智能"], ["机器人","自动化"]),
    ("DeepSeek概念", ["DeepSeek","大模型"], []),
    ("AI智能体", ["AI Agent","智能体","AI助手"], []),
    ("多模态AI", ["多模态","视觉模型","图文"], []),
    ("AI语料", ["数据标注","语料","训练数据","数据集"], []),
    ("AI应用", ["AI应用","智能软件","AI平台","AI解决方案"], []),
    ("AI PC", ["笔记本","PC","电脑","整机"], []),
    ("AI手机", ["手机","移动终端","智能手机"], []),
    ("AI眼镜", ["AR","VR","眼镜","头显","MR","XR"], []),
    # 机器人
    ("机器人概念", ["机器人","机械臂","伺服","控制器","自动化"], []),
    ("人形机器人", ["人形机器人","双足","仿生"], ["工业机器人"]),
    ("减速器", ["减速器","谐波","RV","行星减速"], []),
    ("机器视觉", ["机器视觉","视觉检测","图像识别","AOI","光学检测"], []),
    # 基础设施
    ("液冷服务器", ["液冷","散热","冷却","温控"], []),
    ("数据中心(AIDC)", ["数据中心","IDC","智算中心"], []),
    ("铜缆高速连接", ["铜缆","高速连接器","AEC","ACC","DAC"], []),
    ("PCB概念", ["PCB","电路板","印制板","HDI","载板","覆铜板"], []),
    ("云计算", ["云","Cloud","SaaS","IaaS","PaaS"], []),
    # 通信
    ("5G概念", ["5G","基站","通信设备","射频","天线","滤波器"], []),
    ("6G概念", ["6G","太赫兹"], []),
    # 软件/安全
    ("信创", ["国产替代","自主可控","信创","国产化","安全可靠"], []),
    ("数据要素", ["数据要素","数据资产","数据交易","数据管理"], []),
    ("数据安全", ["数据安全","信息安全","网络安全"], []),
    ("鸿蒙概念", ["鸿蒙","HarmonyOS","华为生态","鸿蒙开发"], []),
    ("国产操作系统", ["操作系统","OS","国产OS","自主系统"], []),
    # 物联网/消费电子
    ("物联网", ["物联网","IoT","智能家居","智慧城市"], []),
    ("消费电子概念", ["消费电子","手机","电脑","平板","可穿戴"], []),
    ("智能穿戴", ["手表","手环","耳机","穿戴"], []),
    ("传感器", ["传感器","MEMS","感知"], []),
    # 半导体设备/材料
    ("中芯国际概念", ["中芯国际","晶圆厂","代工厂"], []),
    ("光刻机", ["光刻机","光刻","EUV","DUV","曝光"], []),
    ("光刻胶", ["光刻胶","光刻材料","电子化学品","显影"], []),
    ("国家大基金持股", ["大基金","国家集成电路"], []),
    # 汽车
    ("无人驾驶", ["自动驾驶","ADAS","激光雷达","毫米波雷达"], []),
    ("激光雷达", ["激光雷达","LiDAR"], []),
]

def verify(stock_name, core_biz, concept_name):
    """判断一个概念对这只股票是真是假"""
    if not core_biz:
        return None  # 无法判断

    biz_lower = (core_biz + stock_name).lower()

    for cname, pos_kw, neg_kw in CONCEPT_RULES:
        if cname != concept_name:
            continue
        # 检查正面匹配
        for kw in pos_kw:
            if kw.lower() in biz_lower:
                # 检查负面排除
                excluded = False
                for nk in neg_kw:
                    if nk.lower() in biz_lower and kw.lower() not in biz_lower.replace(nk.lower(), ""):
                        excluded = True
                        break
                if not excluded:
                    return True  # ✅ 真有业务
                return None  # ⚠️ 有关联但不核心

    return None  # ⚠️ 默认沾边

# 额外的手动映射（覆盖自动判断）
MANUAL_OVERRIDE = {
    # 光模块三杰
    "300308": {"CPO概念": True, "光通信模块": True, "算力概念": True, "F5G概念": True, "5G概念": True, "无人驾驶": False},
    "300502": {"CPO概念": True, "光通信模块": True, "算力概念": True, "英伟达概念": True},
    "300394": {"CPO概念": True, "光通信模块": True, "算力概念": True, "英伟达概念": True},
    # 光芯片
    "688498": {"CPO概念": True, "光通信模块": True, "国产芯片": True},
    "688313": {"CPO概念": True, "光通信模块": True, "国产芯片": True, "光纤概念": False},
    "688205": {"CPO概念": True, "光通信模块": True, "国产芯片": True},
    "688048": {"CPO概念": True, "光通信模块": True, "国产芯片": True},
    "688195": {"CPO概念": True, "光通信模块": True},
    # 光通信
    "002281": {"CPO概念": True, "光通信模块": True, "F5G概念": True, "5G概念": True, "量子科技": None, "国产芯片": None},
    "601869": {"光纤概念": True, "CPO概念": None, "算力概念": None},
    "600487": {"光纤概念": True, "CPO概念": None, "算力概念": None},
    "600522": {"光纤概念": True, "CPO概念": None, "算力概念": None},
    # 芯片
    "688256": {"国产芯片": True, "AI芯片": True, "算力概念": True, "汽车芯片": None},
    "688041": {"国产芯片": True, "AI芯片": True, "算力概念": True},
    "688981": {"国产芯片": True, "中芯国际概念": True, "国家大基金持股": True, "先进封装": None},
    "002371": {"国产芯片": True, "中芯国际概念": True, "国家大基金持股": True},
    "600584": {"国产芯片": True, "先进封装": True, "国家大基金持股": True, "存储芯片": None},
    "002156": {"国产芯片": True, "先进封装": True, "CPO概念": False, "存储芯片": None, "AI PC": None},
    "688525": {"存储芯片": True, "国产芯片": True, "AI PC": None, "AI手机": None, "AI眼镜": None, "机器人概念": False, "先进封装": None},
    "603986": {"存储芯片": True, "国产芯片": True, "MCU芯片": True, "人工智能": None, "AI眼镜": None, "汽车芯片": None},
    "688008": {"国产芯片": True, "存储芯片": True, "算力概念": None},
    "688012": {"国产芯片": True, "中芯国际概念": True, "国家大基金持股": True},
    "603019": {"算力概念": True, "国产芯片": None, "人工智能": None},
    "000977": {"算力概念": True, "人工智能": True, "国产芯片": False},
    "601138": {"算力概念": True, "人工智能": True, "液冷服务器": True, "英伟达概念": True, "机器人概念": None, "CPO概念": False, "消费电子概念": True},
    "002230": {"人工智能": True, "AI应用": True, "多模态AI": True, "AI智能体": True},
    "688017": {"机器人概念": True, "人形机器人": True, "减速器": True, "专精特新": True, "半导体概念": False},
    "002463": {"PCB概念": True, "算力概念": True},
    "002916": {"PCB概念": True, "国产芯片": True},
    "002938": {"PCB概念": True, "消费电子概念": True},
    "600183": {"PCB概念": True, "国产芯片": None},
    "688629": {"铜缆高速连接": True, "算力概念": True, "CPO概念": None},
    "600330": {"国产芯片": None, "机器人概念": None},
    "600667": {"国产芯片": True, "存储芯片": None},
    "603678": {"国产芯片": True, "5G概念": None},
    "688120": {"国产芯片": True, "中芯国际概念": True},
    "688143": {"光纤概念": True, "光通信模块": None},
    "688170": {"国产芯片": True, "中芯国际概念": True},
    "688220": {"国产芯片": True, "5G概念": True, "物联网": True},
    "688766": {"国产芯片": True, "存储芯片": True},
    "688047": {"国产芯片": True, "算力概念": None},
    "002384": {"PCB概念": True, "消费电子概念": True, "国产芯片": None},
    "688001": {"国产芯片": True, "算力概念": None},
    "603501": {"国产芯片": True, "消费电子概念": True, "汽车芯片": True},
    "002415": {"人工智能": True, "机器视觉": True, "物联网": True},
    "002236": {"人工智能": True, "机器视觉": True, "物联网": True},
    "300033": {"人工智能": True, "AI应用": True},
    "002439": {"数据安全": True, "信创": True, "人工智能": None},
    "300454": {"数据安全": True, "信创": True, "云计算": True},
    "000938": {"算力概念": True, "云计算": True, "人工智能": True, "5G概念": True},
    "300394": {"CPO概念": True, "光通信模块": True, "算力概念": True, "英伟达概念": True},
}

def main():
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # For each stock, generate concept list with verification
    total_verified = 0
    for stock in data["stocks"]:
        code = stock["code"]
        name = stock["name"]
        biz = stock.get("core_business", "")

        # Check manual override
        if code in MANUAL_OVERRIDE:
            override = MANUAL_OVERRIDE[code]
            concepts = []
            for cname, verified in override.items():
                concepts.append({"name": cname, "verified": verified, "detail": ""})
            stock["concepts"] = concepts
            total_verified += 1
            continue

        # Auto-verify for stocks we know about
        if biz:
            # Generate concept list from rules
            concepts = []
            seen = set()
            for cname, pos_kw, neg_kw in CONCEPT_RULES:
                if cname in seen:
                    continue
                biz_lower = (biz + name).lower()
                for kw in pos_kw:
                    if kw.lower() in biz_lower:
                        verified = verify(name, biz, cname)
                        concepts.append({"name": cname, "verified": verified, "detail": ""})
                        seen.add(cname)
                        break
            if concepts:
                stock["concepts"] = concepts
                total_verified += 1

    data["updated"] = "2026-06-13T19:00:00+08:00"
    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with_concepts = sum(1 for s in data["stocks"] if s.get("concepts"))
    print(f"Total stocks: {data['total']}")
    print(f"With concept verification: {with_concepts}")
    print(f"Manually mapped: {len(MANUAL_OVERRIDE)}")
    print(f"Auto-verified: {total_verified - len(MANUAL_OVERRIDE)}")

if __name__ == "__main__":
    main()
