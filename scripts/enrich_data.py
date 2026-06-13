#!/usr/bin/env python3
"""补齐 universe.json：概念校验 + 新增核心 AI 股 + 价格刷新"""
import json, os, sys

DATA_DIR = r"C:\soft\agent\ai-dashboard\data"
UNIVERSE_FILE = os.path.join(DATA_DIR, "universe.json")

# 概念标签校验：{code: [(概念名, 校验状态, 说明), ...]}
# verified: True=真有业务, None=沾边但不核心, False=纯蹭热度
CONCEPT_MAP = {
    "600183": [("PCB概念", True, "核心主业覆铜板"), ("芯片概念", None, "PCB上游，间接受益")],
    "600487": [("光纤概念", True, "核心主业"), ("CPO概念", None, "光纤是CPO上游"), ("算力概念", None, "数据中心用光缆")],
    "600522": [("光纤概念", True, "核心主业"), ("CPO概念", None, "光纤是CPO上游"), ("算力概念", None, "数据中心用光缆")],
    "600584": [("芯片概念", True, "核心主业半导体封测"), ("先进封装", True, "SiP/FC封装"), ("国家大基金持股", True, "")],
    "601138": [("算力概念", True, "AI服务器制造龙头"), ("人工智能", True, "AI服务器"), ("液冷服务器", True, "AI服务器液冷方案"), ("英伟达概念", True, "英伟达GPU服务器供应商"), ("机器人概念", None, "工业机器人，非核心"), ("CPO概念", None, "间接关联"), ("苹果概念", True, "富士康代工关系")],
    "601869": [("光纤概念", True, "核心主业"), ("CPO概念", None, "上游光纤供应商"), ("算力概念", None, "数据中心光纤布线")],
    "688008": [("芯片概念", True, "核心主业内存接口芯片"), ("存储芯片", True, "DDR5接口芯片"), ("算力概念", None, "AI服务器内存接口")],
    "688012": [("芯片概念", True, "核心主业半导体设备"), ("中芯国际概念", True, "晶圆厂设备供应商"), ("国家大基金持股", True, "")],
    "688041": [("芯片概念", True, "核心主业DCU芯片"), ("算力概念", True, "AI算力芯片"), ("国产操作系统", None, "国产替代逻辑"), ("华为昇腾", None, "竞争关系")],
    "688048": [("芯片概念", True, "核心主业激光器芯片"), ("CPO概念", True, "EML是CPO核心芯片"), ("光通信", True, "光芯片是光通信核心器件")],
    "688195": [("光通信", True, "核心主业精密光学器件"), ("CPO概念", True, "光器件供光模块厂"), ("算力概念", None, "间接关联")],
    "688205": [("CPO概念", True, "核心主业光芯片/电芯片"), ("光通信", True, "光模块核心芯片"), ("芯片概念", True, "DSP/Driver芯片")],
    "688256": [("芯片概念", True, "核心主业AI芯片"), ("算力概念", True, "AI算力芯片龙头"), ("国产操作系统", None, "国产替代"), ("汽车芯片", None, "车载推理芯片")],
    "688313": [("CPO概念", True, "核心主业PLC/光芯片"), ("光通信", True, "光通信核心器件"), ("芯片概念", True, "光芯片IDM")],
    "688498": [("CPO概念", True, "核心主业EML/DFB光芯片"), ("光通信", True, "光通信核心芯片"), ("芯片概念", True, "光芯片IDM")],
    "688525": [("芯片概念", True, "存储芯片/模组"), ("存储芯片", True, "核心主业"), ("算力概念", None, "AI服务器存储需求")],
    "688629": [("芯片概念", None, "连接器供芯片封装"), ("算力概念", True, "高速连接器供AI服务器"), ("CPO概念", None, "光模块连接器")],
    "688981": [("芯片概念", True, "核心主业晶圆代工"), ("中芯国际概念", True, "晶圆代工龙头"), ("国家大基金持股", True, "")],
    "002156": [("芯片概念", True, "核心主业半导体封测"), ("先进封装", True, "先进封装产能"), ("国家大基金持股", True, "")],
    "002281": [("CPO概念", True, "核心主业光模块"), ("光通信", True, "光通信核心器件"), ("算力概念", True, "AI数据中心用光模块"), ("F5G概念", True, "")],
    "002371": [("芯片概念", True, "核心主业半导体设备"), ("中芯国际概念", True, "晶圆厂设备供应商"), ("国家大基金持股", True, "")],
    "002463": [("PCB概念", True, "核心主业PCB"), ("算力概念", True, "AI服务器PCB龙头"), ("芯片概念", None, "PCB是半导体封装上游")],
    "002916": [("PCB概念", True, "核心主业IC载板"), ("芯片概念", True, "IC载板是芯片封装核心材料"), ("算力概念", None, "AI芯片载板需求")],
    "688017": [("机器人概念", True, "核心主业谐波减速器"), ("人形机器人", True, "人形机器人核心零部件"), ("专精特新", True, "")],
    "600330": [("芯片概念", None, "磁性材料用于芯片电感"), ("机器人概念", None, "磁性材料用于电机")],
    "600667": [("芯片概念", True, "半导体工程EPC"), ("存储芯片", None, "子公司海太半导体")],
    "603678": [("芯片概念", True, "核心主业MLCC被动元件"), ("5G概念", None, "5G基站用MLCC")],
    "603986": [("芯片概念", True, "核心主业NOR Flash/MCU"), ("存储芯片", True, "NOR Flash存储器"), ("MCU芯片", True, "32位MCU"), ("算力概念", None, "存算一体方向")],
    "688120": [("芯片概念", True, "核心主业半导体设备(CMP)"), ("中芯国际概念", True, "晶圆厂设备供应商"), ("国家大基金持股", True, "")],
    "688143": [("光纤概念", True, "核心主业特种光纤"), ("光通信", None, "光纤器件")],
    "688170": [("芯片概念", True, "核心主业半导体检测设备"), ("中芯国际概念", True, "晶圆厂设备供应商")],
    "688220": [("芯片概念", True, "核心主业蜂窝通信芯片"), ("5G概念", True, "5G通信芯片"), ("物联网", True, "物联网芯片")],
    "688766": [("芯片概念", True, "核心主业NOR Flash"), ("存储芯片", True, "存储器芯片")],
    "002384": [("PCB概念", True, "核心主业PCB/精密制造"), ("芯片概念", None, "PCB上游"), ("苹果概念", True, "苹果供应链"), ("算力概念", None, "AI服务器PCB")],
    "688047": [("芯片概念", True, "核心主业国产CPU"), ("国产操作系统", True, "自主指令集"), ("算力概念", None, "国产算力替代")],
    "603019": [("芯片概念", None, "参股海光信息"), ("算力概念", True, "核心主业国产算力服务器"), ("国产操作系统", True, "国产算力平台")],
    "300308": [("CPO概念", True, "核心主业800G/1.6T光模块"), ("光通信", True, "光模块龙头"), ("算力概念", True, "AI数据中心核心供应商"), ("F5G概念", True, ""), ("5G概念", True, ""), ("无人驾驶", None, "仅激光雷达光器件")],
    "300502": [("CPO概念", True, "核心主业高速光模块"), ("光通信", True, "光模块"), ("算力概念", True, "AI数据中心光模块"), ("英伟达概念", True, "英伟达光模块供应商")],
    "300394": [("CPO概念", True, "核心主业光器件(FA/连接器)"), ("光通信", True, "光通信核心器件"), ("算力概念", True, "AI数据中心光器件"), ("英伟达概念", True, "英伟达供应链")],
}

# 需要新增的核心 AI 股（不在自选股里但在全市场很重要）
MISSING_STOCKS = [
    {"code": "300308", "name": "中际旭创", "market": "sz", "core_business": "高速光模块龙头(800G/1.6T)", "category": "optical", "added_price": 1149.0, "added_date": "20260613"},
    {"code": "300502", "name": "新易盛", "market": "sz", "core_business": "高速光模块(800G/LPO)", "category": "optical", "added_price": 503.0, "added_date": "20260613"},
    {"code": "300394", "name": "天孚通信", "market": "sz", "core_business": "光器件龙头(FA/连接器)", "category": "optical", "added_price": 285.0, "added_date": "20260613"},
    {"code": "688981", "name": "中芯国际", "market": "sh", "core_business": "晶圆代工龙头", "category": "chip", "added_price": 145.0, "added_date": "20260613"},
    {"code": "603501", "name": "韦尔股份", "market": "sh", "core_business": "CIS图像传感器龙头", "category": "chip", "added_price": 195.0, "added_date": "20260613"},
    {"code": "688012", "name": "中微公司", "market": "sh", "core_business": "半导体刻蚀设备龙头", "category": "chip", "added_price": 290.0, "added_date": "20260613"},
]

def main():
    # Load current universe
    with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_codes = {s['code'] for s in data['stocks']}

    # Update concepts for existing stocks
    for stock in data['stocks']:
        code = stock['code']
        if code in CONCEPT_MAP:
            stock['concepts'] = [
                {"name": name, "verified": verified, "detail": detail}
                for name, verified, detail in CONCEPT_MAP[code]
            ]

    # Add missing key AI stocks
    added_count = 0
    for ms in MISSING_STOCKS:
        if ms['code'] not in existing_codes:
            stock = {
                "code": ms['code'],
                "name": ms['name'],
                "market": ms['market'],
                "core_business": ms['core_business'],
                "category": ms['category'],
                "price": ms['added_price'],
                "change_pct": 0,
                "market_cap": 0,
                "pe": 0,
                "pb": 0,
                "concepts": CONCEPT_MAP.get(ms['code'], []),
                "latest_news": [],
                "revenue_detail": "",
                "added_price": ms['added_price'],
                "added_date": ms['added_date'],
            }
            data['stocks'].append(stock)
            existing_codes.add(ms['code'])
            added_count += 1

    data['total'] = len(data['stocks'])
    data['updated'] = "2026-06-13T16:00:00+08:00"

    with open(UNIVERSE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Stats
    cat_counts = {}
    concept_count = sum(1 for s in data['stocks'] if s.get('concepts'))
    for s in data['stocks']:
        cat_counts[s['category']] = cat_counts.get(s['category'], 0) + 1
    print(f"Total: {data['total']} stocks (+{added_count} new)")
    print(f"With concepts: {concept_count}")
    print(f"Categories: {cat_counts}")

if __name__ == '__main__':
    main()
