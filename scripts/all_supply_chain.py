#!/usr/bin/env python3
"""全量供应链补全：上游/下游/定位"""
import json

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

# 供应链模板(按业务关键词)
SC_TEMPLATES = {
    "光模块": {"up":"博通/Credo(DSP)+Lumentum/源杰(EML)+三安/仕佳(光芯片)","down":"NVIDIA/Meta/Google/AWS/阿里/华为","pos":"光模块供应商，AI算力互联核心"},
    "光器件": {"up":"光纤/陶瓷/玻璃/金属零件供应商","down":"中际旭创/新易盛/Coherent/光模块厂","pos":"光器件供应商，光模块上游精密元件"},
    "光芯片": {"up":"InP/GaAs衬底+MOCVD设备+光刻胶+气体","down":"中际旭创/新易盛/光迅/华为/中兴","pos":"光芯片供应商，光通信产业链核心环节"},
    "光放大器": {"up":"Marvell/Broadcom(DSP)+Lumentum(泵浦激光器)+住友/长飞(光纤)","down":"华为/中兴/烽火/阿里/腾讯/三大运营商","pos":"光放大器供应商，AI数据中心传输层"},
    "DCI": {"up":"光模块/光放大器/光纤/交换机供应商","down":"阿里/腾讯/百度/字节/运营商","pos":"数据中心互联解决方案商"},
    "光纤": {"up":"高纯四氯化硅/锗/涂料/PE料供应商","down":"三大运营商/中国广电/互联网/海缆厂商","pos":"光纤光缆供应商，通信网络基础设施"},
    "光缆": {"up":"光纤/钢丝/铝带/PE护套料供应商","down":"三大运营商/中国广电/互联网","pos":"光缆供应商，通信网络基础设施"},
    "芯片设计": {"up":"ARM/Synopsys/Cadence(EDA/IP)+台积电/中芯(代工)","down":"消费电子/汽车/物联网/通信设备厂商","pos":"芯片设计公司，半导体产业链上游"},
    "晶圆代工": {"up":"ASML/应材/LAM/TEL(设备)+SUMCO/信越(硅片)+气体/化学品","down":"华为海思/豪威/全志/瑞芯微/寒武纪/比特大陆","pos":"晶圆代工厂，半导体制造核心环节"},
    "封测": {"up":"设备(ASM/Disco)+引线框架/基板/金线/塑封料","down":"高通/AMD/NVIDIA/华为海思/芯片设计公司","pos":"封测服务商，半导体后端工序"},
    "半导体设备": {"up":"精密零部件(阀门/射频/密封/陶瓷)+传感器/电机","down":"中芯国际/华虹/长存/长鑫/士兰微/华润微","pos":"半导体设备供应商，晶圆厂上游"},
    "半导体材料": {"up":"高纯原料(硅粉/气体/金属)+化工设备","down":"中芯国际/华虹/长存/长鑫/半导体厂商","pos":"半导体材料供应商，晶圆厂上游耗材"},
    "EDA": {"up":"计算资源/算法/IP库","down":"芯片设计公司/晶圆厂","pos":"EDA工具供应商，芯片设计必备软件"},
    "PCB": {"up":"生益/南亚/台光(覆铜板)+日矿/福田(铜箔)+油墨/干膜","down":"华为/中兴/浪潮/Apple/NVIDIA(间接)/汽车Tier1","pos":"PCB供应商，电子电路互联基础"},
    "覆铜板": {"up":"电子玻纤布/环氧树脂/铜箔供应商","down":"沪电/深南/鹏鼎/景旺/胜宏等PCB厂商","pos":"覆铜板供应商，PCB核心原材料"},
    "服务器": {"up":"NVIDIA(GPU)+Intel/AMD(CPU)+三星/海力士(内存)+博通(网卡)","down":"BAT/字节/快手/运营商/政府/金融","pos":"服务器厂商，AI算力基础设施核心"},
    "算力": {"up":"NVIDIA/华为(GPU)+服务器/网络/电力","down":"互联网/运营商/政府/金融/科研","pos":"算力服务商，AI训练推理基础设施"},
    "数据中心": {"up":"电力/土地/机柜/空调/网络带宽/UPS供应商","down":"BAT/字节/快手/金融/政府/企业","pos":"IDC服务商，数字基础设施"},
    "液冷": {"up":"压缩机/换热器/冷媒/管路/冷板供应商","down":"BAT/字节/NVIDIA/服务器厂商/储能","pos":"液冷散热方案商，AI服务器散热核心"},
    "连接器": {"up":"铜合金/工程塑料/端子/模具供应商","down":"Apple/华为/小米/汽车Tier1/服务器厂商","pos":"连接器供应商，电子设备互联基础"},
    "传感器": {"up":"MEMS晶圆/ASIC芯片/陶瓷/金属/封装材料","down":"汽车OEM/手机/工业/医疗设备厂商","pos":"传感器供应商，智能感知核心器件"},
    "软件": {"up":"云服务/服务器/数据库/开发工具","down":"企业/政府/教育/金融","pos":"软件服务商，数字化转型赋能者"},
    "AI应用": {"up":"NVIDIA/华为(GPU)+云服务+数据/语料","down":"企业/个人/政府/教育/医疗","pos":"AI应用开发商，大模型技术落地"},
    "安全": {"up":"服务器/网络设备/威胁情报/密码芯片","down":"政府/金融/运营商/军队/能源/企业","pos":"网络安全厂商，数字安全守护者"},
    "机器人": {"up":"减速器/伺服/控制器/传感器/结构件供应商","down":"汽车/3C/锂电/光伏/物流/医疗制造商","pos":"机器人厂商，智能制造核心装备"},
    "减速器": {"up":"轴承钢/齿轮/密封件/润滑脂供应商","down":"工业机器人/人形机器人/机床厂商","pos":"减速器供应商，机器人关节核心部件"},
    "伺服": {"up":"IGBT/编码器/磁钢/铜线/散热件","down":"工业机器人/机床/自动化设备/新能源车","pos":"伺服系统供应商，运动控制核心"},
    "通信设备": {"up":"博通/Intel/高通(芯片)+光模块/天线/结构件","down":"三大运营商/中国广电/互联网/企业","pos":"通信设备商，网络基础设施"},
    "交换机": {"up":"博通/Intel/盛科(交换芯片)+光模块/电源","down":"运营商/互联网/企业/政府","pos":"交换机厂商，数据中心网络核心"},
    "新能源": {"up":"硅料/锂矿/铜箔/IGBT/逆变器芯片","down":"光伏电站/新能源车/储能/电网","pos":"新能源产品供应商"},
    "汽车电子": {"up":"NXP/Infineon/TI(芯片)+PCB/连接器/传感器","down":"比亚迪/特斯拉/蔚来/理想/传统车企","pos":"汽车电子供应商"},
    "消费电子": {"up":"芯片/PCB/电池/结构件/显示屏供应商","down":"Apple/华为/小米/OPPO/vivo/三星","pos":"消费电子供应商"},
}

def get_sc(biz_text, category, name):
    """根据业务关键词匹配供应链模板"""
    for kw, sc in SC_TEMPLATES.items():
        if kw in biz_text or kw in name:
            return sc

    # Category fallback
    cat_sc = {
        "optical": {"up":"光芯片/电芯片/PCB/结构件供应商","down":"光模块厂/设备商/互联网/运营商","pos":"光通信产业链企业"},
        "chip": {"up":"设备/材料/EDA/IP/代工厂","down":"模组厂/整机厂/终端品牌","pos":"半导体产业链企业"},
        "compute": {"up":"GPU/CPU/内存/PCB/电源供应商","down":"互联网/运营商/金融/政府","pos":"AI算力产业链企业"},
        "robot": {"up":"减速器/伺服/控制器/传感器供应商","down":"汽车/3C/物流/医疗制造商","pos":"机器人产业链企业"},
        "app": {"up":"云服务/芯片/数据供应商","down":"企业/政府/个人消费者","pos":"AI应用软件层企业"},
        "infra": {"up":"设备/电力/机柜/带宽供应商","down":"互联网/运营商/金融","pos":"AI基础设施层企业"},
    }
    return cat_sc.get(category, {"up":"上游供应商","down":"下游客户","pos":"产业链参与者"})

def main():
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Count existing supply chain data
    has_sc = sum(1 for s in data["stocks"]
                 if s.get("deep_analysis",{}).get("supply_chain",{}).get("upstream"))

    updated = 0
    for stock in data["stocks"]:
        da = stock.setdefault("deep_analysis", {})
        sc = da.get("supply_chain", {})
        # If already has detailed supply chain (from manual), keep it
        if sc.get("upstream") and len(sc.get("upstream","")) > 20:
            continue

        biz = stock.get("core_business", "")
        name = stock.get("name", "")
        cat = stock["category"]

        template = get_sc(biz, cat, name)
        da["supply_chain"] = {
            "upstream": template["up"],
            "downstream": template["down"],
            "position": template["pos"],
        }
        updated += 1

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with_sc = sum(1 for s in data["stocks"]
                  if s.get("deep_analysis",{}).get("supply_chain",{}).get("upstream"))
    print(f"Updated: {updated}")
    print(f"With supply chain: {with_sc}/{data['total']}")

    # Verify a sample
    for code in ["688205","300476","688525","300033"]:
        s = next(x for x in data["stocks"] if x["code"]==code)
        sc = s["deep_analysis"]["supply_chain"]
        print(f"\n{code} {s['name']}:")
        print(f"  Up: {sc['upstream'][:60]}")
        print(f"  Down: {sc['downstream'][:60]}")
        print(f"  Pos: {sc['position'][:60]}")

if __name__ == "__main__":
    main()
