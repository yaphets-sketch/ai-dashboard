#!/usr/bin/env python3
"""全面修正：名称+核心业务+财报数据"""
import json, os, urllib.request, re
from datetime import datetime

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"
NEWS_DIR = r"C:\soft\agent\ai-dashboard\data\news"

# 精确核心业务（按代码）
ACCURATE_BIZ = {
    # PCB
    "300476": ("AI服务器PCB/HDI板", "chip"),
    "002916": ("IC载板/高多层PCB", "chip"),
    "002463": ("AI服务器PCB龙头", "chip"),
    "002938": ("HDI/类载板/FPC", "chip"),
    "002384": ("FPC/精密制造/PCB", "chip"),
    "600183": ("覆铜板(CCL)/PCB上游材料", "chip"),
    "002436": ("PCB/样板小批量", "chip"),
    "300814": ("PCB/样板", "chip"),
    "300903": ("PCB/HDI板", "chip"),
    "688519": ("覆铜板(CCL)", "chip"),
    "688300": ("石英纤维/半导体材料", "chip"),
    "603228": ("高多层PCB", "chip"),
    "300735": ("PCB/EMS代工", "chip"),
    # 芯片
    "688256": ("国产AI芯片(思元)龙头", "chip"),
    "688041": ("国产DCU/AI加速卡龙头", "chip"),
    "688981": ("晶圆代工龙头(14nm/28nm)", "chip"),
    "002371": ("半导体设备龙头(刻蚀/薄膜)", "chip"),
    "688012": ("半导体刻蚀/CVD设备龙头", "chip"),
    "688072": ("半导体CVD/PVD设备", "chip"),
    "688082": ("半导体清洗设备", "chip"),
    "688120": ("CMP设备/减薄设备", "chip"),
    "688037": ("半导体涂胶显影设备", "chip"),
    "688409": ("半导体设备零部件", "chip"),
    "688361": ("半导体检测/量测设备", "chip"),
    "688627": ("半导体测试设备", "chip"),
    "300604": ("半导体测试分选设备", "chip"),
    "688147": ("半导体薄膜沉积设备", "chip"),
    "600584": ("半导体封测龙头(SiP/FC)", "chip"),
    "002156": ("半导体封测(FC-BGA)", "chip"),
    "002185": ("半导体封测", "chip"),
    "688403": ("半导体封测(面板级)", "chip"),
    "688525": ("存储芯片模组/SSD", "chip"),
    "603986": ("NOR Flash/MCU/DRAM", "chip"),
    "688766": ("NOR Flash存储器", "chip"),
    "688416": ("NOR Flash/MCU", "chip"),
    "300672": ("存储控制芯片", "chip"),
    "688110": ("SLC NAND Flash", "chip"),
    "688008": ("内存接口芯片( DDR5 )龙头", "chip"),
    "603501": ("CIS图像传感器龙头", "chip"),
    "688728": ("CIS/BSI图像传感器", "chip"),
    "603160": ("指纹识别/触控芯片", "chip"),
    "300474": ("GPU芯片(国产)", "chip"),
    "688047": ("国产CPU(龙芯)", "chip"),
    "688001": ("国产CPU(龙芯中科)", "chip"),
    "688521": ("芯片IP授权/设计服务", "chip"),
    "688385": ("FPGA芯片", "chip"),
    "688107": ("FPGA/SoC芯片", "chip"),
    "300327": ("MCU/触控芯片", "chip"),
    "603893": ("端侧AI SoC芯片", "chip"),
    "300458": ("AIoT/平板芯片", "chip"),
    "688262": ("汽车MCU/SoC芯片", "chip"),
    "688220": ("蜂窝通信芯片(Cat1/NB-IoT)", "chip"),
    "300183": ("电力物联网通信芯片", "chip"),
    "688141": ("电源管理芯片", "chip"),
    "688396": ("功率半导体(IGBT/MOSFET)", "chip"),
    "600703": ("化合物半导体(LED/射频)", "chip"),
    "688126": ("大硅片/SOI衬底", "chip"),
    "688019": ("CMP设备/抛光液", "chip"),
    "300101": ("北斗导航芯片/模块", "chip"),
    "688589": ("电力线载波通信芯片", "chip"),
    "688595": ("MCU/SoC芯片", "chip"),
    # 光通信
    "300308": ("高速光模块龙头(800G/1.6T)", "optical"),
    "300502": ("高速光模块(800G/LPO)", "optical"),
    "300394": ("光器件龙头(FA/隔离器/透镜)", "optical"),
    "002281": ("光模块/光器件/光放大器", "optical"),
    "000988": ("光模块/激光设备/传感器", "optical"),
    "688498": ("光芯片IDM(EML/DFB激光器)", "optical"),
    "688313": ("PLC/AWG光芯片", "optical"),
    "688205": ("光通信DSP/Driver芯片", "optical"),
    "688048": ("激光器芯片(EML/DFB)", "optical"),
    "688195": ("精密光学元件/透镜", "optical"),
    "300548": ("PLC分路器/AWG芯片", "optical"),
    "300620": ("光调制器/光器件", "optical"),
    "301205": ("高速光模块/光器件", "optical"),
    "688662": ("TEC热电制冷/光模块散热", "optical"),
    "300570": ("光连接器/适配器", "optical"),
    "301191": ("陶瓷基板/光电器件", "optical"),
    "688143": ("特种光纤/光纤环", "optical"),
    "601869": ("光纤预制棒/光缆龙头", "optical"),
    "600487": ("光纤光缆/海洋通信/海缆", "optical"),
    "600522": ("光纤光缆/海缆/光伏", "optical"),
    "600345": ("光纤光缆/接入网", "optical"),
    "000070": ("光纤光缆/光通信设备", "optical"),
    "600498": ("通信设备/光纤缆", "optical"),
    "603083": ("光模块/通信设备", "optical"),
    "300913": ("高速连接器(铜缆/AEC)", "optical"),
    # AI算力
    "601138": ("AI服务器/云计算/智能制造", "compute"),
    "603019": ("国产算力服务器/高性能计算", "compute"),
    "000977": ("AI服务器龙头/云计算", "compute"),
    "000938": ("网络设备/服务器/云计算", "compute"),
    "002261": ("华为AI算力/软硬一体", "compute"),
    "000066": ("国产计算/服务器/整机", "compute"),
    "000034": ("IT分销/云计算服务", "compute"),
    "600100": ("AI服务器/信创整机", "compute"),
    "002152": ("AI服务器/金融科技", "compute"),
    "300857": ("AI训推一体机/存储", "compute"),
    "600602": ("算力/云服务/智慧城市", "compute"),
    "603220": ("AI算力租赁/5G新基建", "compute"),
    "002368": ("信创整机/AI服务器", "compute"),
    # 液冷/基础设施
    "688629": ("高速连接器/液冷连接", "infra"),
    "300383": ("IDC数据中心/云计算", "infra"),
    "603881": ("IDC数据中心服务", "infra"),
    "600845": ("工业互联网/IDC", "infra"),
    "600804": ("IDC数据中心/宽带", "infra"),
    "002837": ("精密温控/液冷龙头", "infra"),
    "300499": ("液冷板/散热设备", "infra"),
    "301018": ("精密温控/液冷", "infra"),
    "002050": ("热管理/液冷组件", "infra"),
    "002518": ("UPS电源/数据中心", "infra"),
    "002475": ("连接器/线缆/消费电子代工", "infra"),
    "603118": ("通信设备/交换机/路由器", "infra"),
    # 机器人
    "688017": ("谐波减速器龙头(人形机器人核心)", "robot"),
    "002747": ("工业机器人/协作机器人", "robot"),
    "300124": ("伺服驱动器/机器人", "robot"),
    "002527": ("工业机器人/自动化", "robot"),
    "002896": ("精密减速器(RV/谐波)", "robot"),
    "603728": ("电机/运动控制/机器人", "robot"),
    "300024": ("工业机器人龙头", "robot"),
    "300607": ("工业机器人/注塑自动化", "robot"),
    "688160": ("运动控制/低压伺服", "robot"),
    "688305": ("五轴数控机床/机器人减速器", "robot"),
    # AI应用
    "002230": ("AI大模型(星火)/语音龙头", "app"),
    "688111": ("AI办公软件(WPS)/大模型", "app"),
    "300033": ("金融AI/智能投顾", "app"),
    "300059": ("金融数据/互联网券商", "app"),
    "600570": ("金融IT/智能投顾", "app"),
    "300418": ("AI大模型/浏览器/搜索", "app"),
    "601360": ("AI搜索/网络安全", "app"),
    "688327": ("AI视觉/人机协同平台", "app"),
    "300624": ("AI创意软件/视频编辑", "app"),
    "300170": ("企业数字化/AI Agent", "app"),
    "300229": ("NLP/大数据/AI搜索", "app"),
    "002415": ("AI视觉/安防龙头", "app"),
    "002236": ("AI视觉/安防", "app"),
    "688088": ("AI视觉算法/手机影像", "app"),
    "688777": ("工业自动化/DCS龙头", "app"),
    "600588": ("企业ERP/云服务/智能体", "app"),
    "300378": ("智能制造软件/ERP", "app"),
    "300687": ("智能制造/工业软件", "app"),
    "300212": ("数据资产/蓝光存储", "app"),
    "300166": ("大数据/工业互联网", "app"),
    "002212": ("网络安全/密码安全龙头", "app"),
    "300369": ("网络安全", "app"),
    "300188": ("网络安全/取证/大数据", "app"),
    "688561": ("网络安全龙头", "app"),
    "300496": ("智能驾驶OS/座舱", "app"),
    "002920": ("智能驾驶域控龙头", "app"),
    "002405": ("高精地图/智能驾驶", "app"),
    "300598": ("智能驾驶/座舱软件", "app"),
    "300253": ("医疗信息化/AI医疗", "app"),
    "300451": ("医疗信息化", "app"),
    "688246": ("医疗信息化/AI辅助诊断", "app"),
    "002373": ("智能交通/车路协同", "app"),
    "300248": ("智慧校园/AI教育", "app"),
    "603927": ("AI应用软件/AI中台", "app"),
    "002609": ("智慧停车/AI交通", "app"),
    "300659": ("数据安全/隐私计算", "app"),
    "603039": ("协同办公/AI智能体", "app"),
    "688369": ("协同办公/AI流程自动化", "app"),
    "300682": ("电力信息化/AI应用", "app"),
    "300770": ("视频AI/大视频", "app"),
    "300674": ("银行IT/金融科技", "app"),
    "688316": ("云计算/私有云", "app"),
    "688158": ("云计算/公有云", "app"),
    "688229": ("AI监控/APM性能管理", "app"),
    "300785": ("AI购物助手/消费决策", "app"),
    "300552": ("智能交通/ETC", "app"),
    "300773": ("支付终端/AI智能体", "app"),
    "300790": ("AI视觉/智慧金融", "app"),
    "300359": ("在线教育/AI教育", "app"),
    "300559": ("教育信息化/AI评测", "app"),
    "600536": ("行业应用软件/AI", "app"),
    "300168": ("智慧城市/医疗IT/AI", "app"),
    "300020": ("智慧城市/智慧交通", "app"),
    "300730": ("电子政务/信创OA", "app"),
    "002279": ("电子政务/大数据", "app"),
    "002268": ("密码安全/数据加密", "app"),
    "002439": ("网络安全/安全运营", "app"),
    "600718": ("智慧城市/智能汽车/医疗IT", "app"),
    "600850": ("行业数字化/IT服务", "app"),
    "600410": ("云计算/IT服务/AI算力", "app"),
    "600756": ("电子政务/信创", "app"),
    "300634": ("企业邮箱/AI办公", "app"),
    "300925": ("IT外包/AI应用开发", "app"),
    "301171": ("跨境营销/AI广告", "app"),
    "301396": ("智慧城市/智慧医疗", "app"),
    "301236": ("数字技术服务/AI应用", "app"),
    "300379": ("基础软件/中间件", "app"),
    "300366": ("大数据/数据库/信创", "app"),
    "002065": ("IT服务/智慧城市", "app"),
    "600476": ("电子政务/邮政信息化", "app"),
    "000158": ("智慧城市/纺织", "app"),
    "300603": ("通信技术服务/算力", "app"),
    "300608": ("电信软件/大数据", "app"),
    "300687": ("智能制造/工业软件", "app"),
    "300925": ("IT外包服务", "app"),
    "301316": ("IT外包/AI应用", "app"),
    "300113": ("游戏/电竞/AI", "app"),
    "300085": ("金融科技/数字货币", "app"),
    "300249": ("数据中心设备/温控", "app"),
    # 消费电子/元器件
    "000725": ("面板龙头(OLED/LCD)", "chip"),
    "002008": ("激光设备龙头", "optical"),
    "600330": ("磁性材料/蓝宝石衬底", "chip"),
    "600667": ("半导体EPC/工程总包", "chip"),
    "002119": ("引线框架/半导体材料", "chip"),
    "603678": ("MLCC瓷介电容", "chip"),
    "300408": ("陶瓷基片/MLCC/光纤插芯", "chip"),
    "002138": ("电感/变压器/被动元件", "chip"),
    "002484": ("铝电解电容/薄膜电容", "chip"),
    "688322": ("3D视觉传感器", "chip"),
    "300433": ("玻璃盖板/蓝宝石", "other"),
    "601208": ("绝缘材料/光学膜", "other"),
    "603256": ("电子玻璃纤维布", "chip"),
    "603773": ("玻璃基板/光掩模", "chip"),
    "300395": ("石英玻璃/半导体材料", "chip"),
    "300136": ("天线/射频/EMC", "chip"),
    "002241": ("声学/AI耳机/VR", "other"),
    "002475": ("连接器/线缆/代工", "infra"),
    "300115": ("精密功能件/结构件", "other"),
    "002402": ("智能控制器", "other"),
    "002456": ("光学镜头/车载镜头", "optical"),
    "002273": ("光学镜头/红外镜头", "optical"),
    "300207": ("电池Pack/消费电子", "other"),
    "601231": ("SiP封装/模组代工", "chip"),
    "300555": ("通信设备/物联网终端", "infra"),
    "002544": ("通信网络规划/设计", "infra"),
    "300476": ("AI服务器PCB/HDI", "chip"),
    "688595": ("MCU/SoC芯片", "chip"),
}

# Q1 2026 财报数据（收入/净利润 亿元）
Q1_DATA = {
    "601138": (2510.78, 105.95),
    "000977": (354.70, 6.05),
    "300308": (None, None),  # TBD
    "300502": (83.38, 27.80),
    "688256": (28.85, 10.13),
    "688041": (None, None),
    "688981": (176.17, 13.61),
    "002371": (103.23, 16.35),
    "603019": (31.99, 2.28),
    "002230": (52.74, -1.70),
    "603986": (41.88, 14.61),
    "688008": (14.61, 8.47),
    "688498": (3.55, 1.79),
    "002938": (79.86, 4.63),
    "002384": (131.38, 11.10),
    "688012": (None, None),
    "688072": (None, None),
    "688525": (None, None),
    "002916": (None, None),
    "002463": (None, None),
    "002156": (None, None),
    "600584": (None, None),
    "688048": (None, None),
    "688017": (None, None),
    "600487": (None, None),
    "601869": (None, None),
    "600522": (None, None),
    "603083": (None, None),
}

def fix_names_via_tencent(stocks):
    """用腾讯API批量获取真实名称"""
    # Build lookup of codes that need names
    need_names = [s for s in stocks if s['name'] == s['code'] or len(s['name']) <= 6]
    if not need_names:
        return 0

    # Batch query (50 at a time)
    updated = 0
    for i in range(0, len(need_names), 50):
        batch = need_names[i:i+50]
        market_codes = [f"sh{c['code']}" if c['code'].startswith('6') else f"sz{c['code']}" for c in batch]
        url = f"http://qt.gtimg.cn/q={','.join(market_codes)}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            r = urllib.request.urlopen(req, timeout=10)
            data = r.read().decode("gbk", errors="replace")
            for line in data.split("\n"):
                m = re.search(r'"([^"]+)"', line)
                if not m: continue
                parts = m.group(1).split("~")
                if len(parts) < 3: continue
                code = parts[2].strip()
                name = parts[1].strip()
                for s in batch:
                    if s['code'] == code and s['name'] == code:
                        s['name'] = name
                        updated += 1
        except: pass
    return updated

def main():
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Fix names via Tencent
    named = fix_names_via_tencent(data["stocks"])
    print(f"Names fixed: {named}")

    # 2. Fix core business + category
    biz_fixed = 0
    for stock in data["stocks"]:
        code = stock["code"]
        if code in ACCURATE_BIZ:
            biz, cat = ACCURATE_BIZ[code]
            stock["core_business"] = biz
            if stock["category"] != cat:
                stock["category"] = cat
            biz_fixed += 1
    print(f"Biz fixed: {biz_fixed}")

    # 3. Add Q1 financial data
    fin_added = 0
    for stock in data["stocks"]:
        code = stock["code"]
        if code in Q1_DATA:
            rev, profit = Q1_DATA[code]
            stock["q1_revenue"] = rev
            stock["q1_profit"] = profit
            fin_added += 1
    print(f"Q1 data added: {fin_added}")

    # 4. Re-verify concepts
    from full_auto_concepts import MANUAL as manual_base
    for stock in data["stocks"]:
        code = stock["code"]
        if code in manual_base:
            stock["concepts"] = [{"name": k, "verified": v, "detail": ""} for k, v in manual_base[code].items()]

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    from collections import Counter
    cats = Counter(s["category"] for s in data["stocks"])
    with_biz = sum(1 for s in data["stocks"] if s.get("core_business"))
    with_q1 = sum(1 for s in data["stocks"] if s.get("q1_revenue") is not None)
    print(f"\nTotal: {data['total']}")
    print(f"With biz: {with_biz}")
    print(f"With Q1: {with_q1}")
    print(f"Categories: {dict(cats)}")

if __name__ == "__main__":
    main()
