#!/usr/bin/env python3
"""
深度产品技术分析引擎
按股票代码返回：核心技术/产品、供应链位置、研发进展、上涨逻辑、竞争格局
"""
import json

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

# 深度分析数据（按代码）
DEEP_DATA = {
    "688205": {
        "products": [
            {"name": "EDFA光放大器", "status": "量产", "detail": "核心产品，用于长距光传输"},
            {"name": "拉曼光纤放大器", "status": "量产", "detail": "超长距传输"},
            {"name": "光模块(100G/400G/800G)", "status": "量产", "detail": "数据中心互联"},
            {"name": "DCI子系统(数据中心互联)", "status": "量产", "detail": "点对点/环形组网，AI数据中心核心需求"},
            {"name": "DSP芯片", "status": "外购", "detail": "光模块DSP从Marvell/Broadcom/Credo采购，无自研DSP"},
            {"name": "高速光电收发芯片", "status": "研发中", "detail": "经营范围含高速光电收发芯片，推测driver/TIA方向"},
        ],
        "supply_chain": {
            "upstream": ["Marvell( DSP )", "Broadcom( DSP )", "Credo( DSP )", "Lumentum(激光器)", "住友(光纤)"],
            "downstream": ["华为", "中兴", "烽火", "阿里/腾讯(AI数据中心)", "中国移动/电信/联通"],
            "position": "光放大器和光模块供应商，处于AI算力传输层核心位置",
        },
        "catalysts": [
            "AI数据中心建设→DCI子系统需求爆发",
            "800G/1.6T光模块升级周期→光放大器配套需求",
            "东数西算工程→长距光传输需求",
            "国产替代→与华为/中兴深度绑定",
            "Q1营收+28%净利润+35%→业绩加速",
        ],
        "risks": [
            "DSP芯片完全依赖进口( Marvell/Broadcom )，供应链风险",
            "光放大器市场规模有限（vs光模块），天花板较低",
            "竞争加剧：光迅/烽火等也有光放大器产品线",
        ],
        "tech_level": {
            "DSP": "无自研，完全外购——这是核心短板",
            "DCI": "有成熟产品，是AI数据中心互联核心受益标的",
            "光芯片": "driver/TIA方向研发中，尚未量产",
            "800G": "有800G光模块产品，但非核心收入来源",
        },
    },
    "300308": {
        "products": [
            {"name": "800G光模块", "status": "量产", "detail": "主力产品，供货NVIDIA/Google/Meta"},
            {"name": "1.6T光模块", "status": "量产/爬坡", "detail": "2026Q3量产，业界最先"},
            {"name": "400G光模块", "status": "成熟", "detail": "传统数据中心主力"},
            {"name": "硅光模块", "status": "研发/小批量", "detail": "硅光子技术路线"},
            {"name": "相干光模块", "status": "量产", "detail": "DCI/长途传输"},
        ],
        "supply_chain": {
            "upstream": ["博通(DSP)", "Credo(DSP)", "Lumentum(EML)", "三安/仕佳(光芯片国产替代)"],
            "downstream": ["NVIDIA(最大客户)", "Google", "Meta", "Microsoft", "AWS"],
            "position": "全球光模块龙头，AI算力核心供应商",
        },
        "catalysts": [
            "NVIDIA GB300/VR200→1.6T需求爆发",
            "北美CSP资本开支持续增长",
            "硅光/CPO技术演进",
        ],
        "risks": ["DSP芯片依赖博通", "地缘政治风险(1260H清单)", "竞争：新易盛/Coherent"],
        "tech_level": {"DSP":"外购博通/Credo，但自研driver芯片已量产","CPO":"有CPO研发，尚未量产","硅光":"研发中"},
    },
    "688498": {
        "products": [
            {"name": "EML激光器芯片(100G/200G)", "status": "量产", "detail": "国内稀缺IDM光芯片"},
            {"name": "DFB激光器芯片", "status": "量产", "detail": "接入网/5G前传"},
            {"name": "CW光源(硅光用)", "status": "研发/小批量", "detail": "硅光模块核心光源"},
            {"name": "探测器芯片", "status": "量产", "detail": "PD/APD芯片"},
        ],
        "supply_chain": {
            "upstream": ["衬底(InP)", "气体", "光刻胶"],
            "downstream": ["中际旭创", "新易盛", "光迅科技", "华为", "中兴"],
            "position": "国内唯一EML IDM厂商，光芯片国产替代核心标的",
        },
        "catalysts": ["EML国产替代", "800G/1.6T对EML需求倍增", "硅光CW光源需求", "Q1营收+大增长"],
        "risks": ["InP衬底依赖进口", "良率爬坡", "海外巨头(Lumentum/三菱)竞争"],
        "tech_level": {"EML":"国内唯一IDM量产","硅光CW":"研发中小批量","DSP":"不做"},
    },
    "688041": {
        "products": [
            {"name": "海光DCU(深算系列)", "status": "量产", "detail": "国产AI加速卡，兼容CUDA生态"},
            {"name": "海光CPU(7000/5000系列)", "status": "量产", "detail": "x86兼容服务器CPU"},
        ],
        "supply_chain": {
            "upstream": ["AMD(x86授权)", "台积电/中芯国际(代工)"],
            "downstream": ["浪潮", "曙光", "联想", "三大运营商", "百度/阿里/腾讯"],
            "position": "国产AI芯片龙头，CPU+DCU双轮驱动",
        },
        "catalysts": ["国产AI算力替代", "美国制裁加速国产化", "互联网大厂采购增加"],
        "risks": ["x86授权到期风险", "先进制程受限", "寒武纪/昇腾竞争"],
        "tech_level": {"DCU":"国内领先，兼容ROCm","CPU":"x86兼容，性能中等","自研架构":"基于AMD Zen1授权改进"},
    },
    "002920": {
        "products": [
            {"name": "智能座舱域控制器", "status": "量产", "detail": "高通8155/8295平台"},
            {"name": "智能驾驶域控制器", "status": "量产/爬坡", "detail": "基于Orin/Thor平台"},
            {"name": "车载信息娱乐系统", "status": "成熟", "detail": "传统主业"},
            {"name": "T-Box/网关", "status": "量产", "detail": "车联网"},
        ],
        "supply_chain": {
            "upstream": ["高通(座舱芯片)", "NVIDIA(智驾芯片)", "TI/英飞凌(MCU)"],
            "downstream": ["理想", "小鹏", "大众", "丰田", "广汽"],
            "position": "国内智能座舱/智驾域控龙头，Tier1",
        },
        "catalysts": ["智能驾驶渗透率提升", "新势力/传统车企智驾竞赛", "舱驾融合趋势"],
        "risks": ["车企自研域控(华为/比亚迪)", "芯片供应依赖高通/NVIDIA", "价格战压力", "Q1营利双降"],
        "tech_level": {"自动驾驶":"L2+域控量产","舱驾一体":"研发中","自研芯片":"无"},
    },
}

# 按概念关键词自动生成简化版分析
AUTO_RULES = {
    "optical": {
        "products": [{"name": "光通信器件/模块", "status": "量产", "detail": "光通信产业链"}],
        "catalysts": ["AI数据中心建设→光通信需求", "800G/1.6T升级周期"],
        "key_question": "是否有自研光芯片（EML/DFB/DSP）？这是光模块公司核心竞争壁垒",
    },
    "chip": {
        "products": [{"name": "芯片/半导体产品", "status": "量产", "detail": "半导体产业链"}],
        "catalysts": ["国产替代", "AI算力芯片需求"],
        "key_question": "制程节点？是否受美国制裁影响？客户是谁？",
    },
    "compute": {
        "catalysts": ["AI算力需求爆发", "数据中心资本开支增长"],
        "key_question": "核心芯片来源（英伟达/华为/自研）？液冷方案？",
    },
    "robot": {
        "catalysts": ["人形机器人产业化", "制造业自动化升级"],
        "key_question": "核心零部件自研率？客户进展？特斯拉/华为供应链？",
    },
    "app": {
        "catalysts": ["AI应用商业化", "大模型落地"],
        "key_question": "AI收入占比？是否接入DeepSeek/OpenClaw等大模型？",
    },
}

def main():
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for stock in data["stocks"]:
        code = stock["code"]
        if code in DEEP_DATA:
            stock["deep_analysis"] = DEEP_DATA[code]
            updated += 1
        else:
            # Auto-generate from category rules
            cat = stock["category"]
            if cat in AUTO_RULES:
                stock["deep_analysis"] = AUTO_RULES[cat]
            else:
                stock["deep_analysis"] = {"key_question": "待深度分析"}

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Deep analysis: {len(DEEP_DATA)} detailed + auto for {len(data['stocks'])-len(DEEP_DATA)}")
    print(f"Detailed: {list(DEEP_DATA.keys())}")

if __name__ == "__main__":
    main()
