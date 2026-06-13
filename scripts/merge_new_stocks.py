"""合并Web搜索到的全部AI概念股"""
import json, re, os
from collections import Counter

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

NEW_CODES = {
    # AI算力芯片
    '300474': ('GPU芯片','chip'), '603893': ('端侧AI芯片','chip'), '300458': ('AIoT芯片','chip'),
    # AI服务器
    '002152': ('AI服务器','compute'), '600100': ('AI服务器','compute'),
    # 液冷
    '300499': ('液冷温控','infra'), '301018': ('液冷温控','infra'), '002837': ('液冷温控龙头','infra'),
    # AI大模型/应用
    '300418': ('AI大模型','app'), '688327': ('AI平台/Agent','app'), '300624': ('AI创意软件','app'),
    '688777': ('工业AI/自动化','robot'), '002747': ('工业机器人','robot'),
    '300059': ('金融AI','app'), '002405': ('智能驾驶/地图','app'),
    '300496': ('智能驾驶/OS','app'), '688369': ('协同办公/AI','app'),
    '603039': ('协同办公/AI','app'), '300170': ('企业数字化/AI Agent','app'),
    '603220': ('算力租赁','compute'), '300773': ('AI智能体','app'),
    '300785': ('AI购物助手','app'), '300857': ('AI训推平台/服务器','compute'),
    '600602': ('算力/云服务','compute'), '600536': ('AI应用/软件','app'),
    '002368': ('信创/AI服务器','compute'), '688229': ('AI监控/APM','app'),
    '300359': ('AI教育','app'), '300248': ('AI校园','app'),
    '300559': ('AI教育','app'), '002212': ('数据安全','app'),
    '002609': ('AI交通','app'), '300253': ('AI医疗','app'),
    '300451': ('AI医疗','app'), '300550': ('AI医疗','app'),
    '688246': ('AI医疗','app'), '300290': ('AI医疗','app'),
    # 芯片/半导体补充
    '688396': ('功率半导体','chip'), '603160': ('指纹芯片','chip'),
    '688728': ('CIS芯片','chip'), '688385': ('FPGA芯片','chip'),
    '688107': ('FPGA芯片','chip'), '300327': ('MCU芯片','chip'),
    '688082': ('半导体设备','chip'), '300604': ('半导体设备','chip'),
    '688037': ('半导体设备','chip'), '688019': ('CMP设备','chip'),
    '688106': ('特种气体/半导体','chip'), '688110': ('NAND芯片','chip'),
    '688403': ('封测','chip'), '688549': ('电子特气','chip'),
    '688409': ('半导体设备','chip'), '688147': ('半导体设备','chip'),
    '688300': ('石英材料/半导体','chip'), '688596': ('电子特气','chip'),
    '600703': ('化合物半导体','chip'), '688141': ('电源芯片','chip'),
    '603005': ('封装/TSV','chip'), '688126': ('硅片/半导体','chip'),
    '688361': ('半导体检测','chip'), '300672': ('存储芯片','chip'),
    '688627': ('半导体检测','chip'), '688110': ('NAND芯片','chip'),
    # 消费电子/PCB
    '002475': ('消费电子/连接器','infra'), '300433': ('消费电子/玻璃','other'),
    '300476': ('AI服务器PCB','chip'), '002456': ('光学镜头','optical'),
    '002138': ('电感/被动元件','chip'), '002241': ('声学/AI耳机','other'),
    '002273': ('光学镜头','optical'), '002402': ('智能控制器','other'),
    '002544': ('通信网络','infra'), '603228': ('PCB','chip'),
    '300735': ('PCB/EMS','chip'), '300555': ('通信设备','infra'),
    '601231': ('SiP封装/消费电子','chip'),
    # 机器人/自动化
    '603728': ('电机/机器人','robot'), '300124': ('伺服/机器人','robot'),
    '002527': ('机器人','robot'), '002896': ('减速器/机器人','robot'),
    '300607': ('工业机器人','robot'), '300024': ('工业机器人','robot'),
    # AI应用
    '002373': ('AI交通','app'), '300552': ('AI交通','app'),
    '300790': ('AI视觉','app'), '002284': ('智能驾驶','app'),
    '002869': ('ETC/智能交通','app'), '300659': ('数据安全','app'),
    '603927': ('AI软件','app'), '300682': ('AI应用','app'),
    '300183': ('通信芯片','chip'), '300770': ('视频技术','app'),
    '300598': ('智能驾驶','app'), '300674': ('金融AI','app'),
    # 光通信
    '688662': ('TEC/光通信','optical'), '688589': ('通信芯片','chip'),
    '300101': ('北斗/军工芯片','chip'), '600498': ('通信设备/光纤','optical'),
    # 液冷/电源
    '002050': ('热管理/液冷','infra'), '002518': ('UPS电源/算力','infra'),
    # 软件/安全
    '688246': ('AI医疗','app'), '300115': ('精密结构件','other'),
    '300207': ('消费电子电池','other'),
}

def main():
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing = {s["code"] for s in data["stocks"]}

    new_codes = set(NEW_CODES.keys()) - existing
    print(f"Existing: {len(existing)}")
    print(f"New: {len(new_codes)}")

    for code in sorted(new_codes):
        biz, cat = NEW_CODES.get(code, ("", "other"))
        data["stocks"].append({
            "code": code, "name": code, "market": "sh" if code.startswith("6") else "sz",
            "core_business": biz, "category": cat,
            "price": 0, "change_pct": 0, "market_cap": 0, "pe": 0, "pb": 0,
            "concepts": [], "latest_news": [], "revenue_detail": "",
            "added_price": 0, "added_date": "20260613",
        })

    data["total"] = len(data["stocks"])
    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    cats = Counter(s["category"] for s in data["stocks"])
    print(f"Total: {data['total']}")
    print(f"Categories: {dict(cats)}")

if __name__ == "__main__":
    main()
