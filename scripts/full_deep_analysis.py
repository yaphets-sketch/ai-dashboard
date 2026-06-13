#!/usr/bin/env python3
"""
全量深度分析引擎：根据赛道+业务关键词自动生成产品/供应链/催化/风险
"""
import json

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

# 手动深度分析（优先）
MANUAL = {
    "688205": {"products":[("EDFA光放大器","量产","核心收入来源"),("拉曼光纤放大器","量产","超长距"),("DCI子系统","量产","AI数据中心互联核心产品"),("光模块100G/400G/800G","量产","数据中心"),("DSP芯片","外购","从Marvell/Broadcom/Credo采购，无自研"),("高速光电收发芯片driver/TIA","研发中","推测在driver方向")],"supply_chain":{"up":"Marvell/Broadcom(DSP)+Lumentum(激光器)+住友(光纤)","down":"华为/中兴/烽火/阿里/腾讯AI数据中心/三大运营商","pos":"光放大器+DCI子系统供应商，AI传输层核心"},"catalysts":["AI数据中心→DCI需求爆发","800G/1.6T→光放大器配套","东数西算→长距传输","国产替代→绑定华为中兴","Q1营收+28%利润+35%→业绩加速"],"risks":["DSP完全依赖进口(核心短板)","光放大器市场规模有限","光迅/烽火竞争"],"key_q":"DSP芯片是否自研？driver/TIA研发进度？DCI订单规模？"},
    "300308": {"products":[("800G光模块","量产","主力，供NVIDIA/Google/Meta"),("1.6T光模块","量产爬坡","2026Q3量产"),("400G光模块","成熟","传统主力"),("硅光模块","研发小批量","硅光子路线"),("相干光模块","量产","DCI/长途")],"supply_chain":{"up":"博通/Credo(DSP)+Lumentum(EML)+三安/仕佳(国产芯片)","down":"NVIDIA(最大客户)/Google/Meta/Microsoft/AWS","pos":"全球光模块龙头"},"catalysts":["NVIDIA GB300/VR200→1.6T需求","北美CSP资本开支增长","硅光/CPO技术演进"],"risks":["DSP依赖博通","1260H地缘风险","新易盛/Coherent竞争"],"key_q":"1.6T量产进度？1260H清单影响？硅光/CPO布局？"},
    "300502": {"products":[("800G光模块","量产","主力产品"),("LPO光模块","量产","低功耗方案"),("1.6T光模块","研发中","预研阶段")],"supply_chain":{"up":"博通/Credo(DSP)+Lumentum/源杰(EML)","down":"NVIDIA/Meta/Microsoft/AWS","pos":"全球第二大光模块供应商"},"catalysts":["H股上市→拓宽融资","800G出货量增长","LPO差异化路线"],"risks":["DSP依赖博通","中际旭创规模优势","实控人协议调整"],"key_q":"H股上市后资金用途？1.6T进度？LPO市场份额？"},
    "688498": {"products":[("EML激光器芯片100G/200G","量产","国内唯一IDM"),("DFB激光器芯片","量产","接入网/5G"),("CW光源硅光用","研发小批量","硅光核心光源"),("探测器芯片PD/APD","量产","光接收")],"supply_chain":{"up":"InP衬底+气体+光刻胶","down":"中际旭创/新易盛/光迅/华为/中兴","pos":"国内唯一EML IDM，光芯片国产替代核心"},"catalysts":["EML国产替代(稀缺性)","800G/1.6T对EML需求倍增","硅光CW光源需求"],"risks":["InP衬底依赖进口","良率爬坡","Lumentum/三菱竞争"],"key_q":"EML产能扩张进度？CW光源客户认证？"},
    "688041": {"products":[("海光DCU深算系列","量产","国产AI加速卡，兼容ROCm"),("海光CPU7000/5000系列","量产","x86兼容")],"supply_chain":{"up":"AMD(x86授权)+台积电/中芯(代工)","down":"浪潮/曙光/联想/运营商/百度阿里腾讯","pos":"国产AI芯片龙头，CPU+DCU双轮"},"catalysts":["国产AI算力替代(制裁加速)","互联网大厂采购增加","市值突破8000亿→龙头溢价"],"risks":["x86授权到期风险","先进制程受限","寒武纪/昇腾竞争"],"key_q":"DCU与昇腾/寒武纪性能对比？x86授权续约？先进封装方案？"},
    "688256": {"products":[("思元AI芯片","量产","国产AI训练/推理芯片"),("边缘AI芯片","量产","端侧推理")],"supply_chain":{"up":"台积电/中芯(代工)","down":"互联网/运营商/政府","pos":"国产AI芯片独角兽，首次扭亏为盈"},"catalysts":["国产替代加速","Q1营收+160%利润扭亏","大模型训练需求"],"risks":["先进制程受限","华为昇腾竞争","生态不如CUDA"],"key_q":"思元最新一代性能？软件生态建设进度？"},
    "601138": {"products":[("AI服务器","量产","全球最大AI服务器制造商"),("云计算","量产","富士康工业互联网"),("智能制造","量产","灯塔工厂")],"supply_chain":{"up":"NVIDIA(GPU)+Intel(CPU)+三星(内存)","down":"NVIDIA/Apple/Amazon/Microsoft","pos":"全球AI服务器代工龙头"},"catalysts":["AI服务器出货高增","NVIDIA深度合作","Q1营收2510亿利润106亿"],"risks":["代工利润薄","地缘政治风险","客户集中(NVIDIA)"],"key_q":"AI服务器份额？液冷布局？智能制造占比？"},
    "688981": {"products":[("14nm/28nm晶圆代工","量产","成熟制程主力"),("N+1/N+2先进制程","量产","先进制程突破"),("CIS/PMIC/MCU代工","成熟","特色工艺")],"supply_chain":{"up":"ASML/应材/泛林(设备)+SUMCO(硅片)","down":"华为/豪威/比亚迪/全志/瑞芯微","pos":"中国大陆最大晶圆代工厂"},"catalysts":["国产替代核心","收购中芯北方49%股权","设备国产化推进"],"risks":["美国制裁设备限制","先进制程与台积电差距","产能利用率波动"],"key_q":"N+2良率？设备国产化率？产能扩张计划？"},
    "002371": {"products":[("刻蚀设备","量产","ICP/CCP刻蚀"),("薄膜沉积设备","量产","PVD/CVD/ALD"),("清洗设备","量产","单晶圆清洗"),("热处理设备","量产","退火/氧化")],"supply_chain":{"up":"零部件(密封/阀门/射频电源)","down":"中芯国际/华虹/长存/长鑫/华润微","pos":"国内半导体设备龙头，平台化布局"},"catalysts":["国产替代核心设备","先进制程扩产","品类持续扩展"],"risks":["零部件进口依赖","技术差距(与AMAT/LAM)","下游资本开支周期"],"key_q":"先进制程设备进展？国产零部件替代率？订单可见度？"},
    "688012": {"products":[("介质刻蚀设备","量产","CCP刻蚀"),("硅刻蚀设备","量产","ICP刻蚀"),("MOCVD设备","量产","化合物半导体")],"supply_chain":{"up":"零部件+气体","down":"中芯国际/华虹/三安/晶合/长江存储","pos":"国内刻蚀设备龙头"},"catalysts":["3D NAND/先进逻辑扩产","化合物半导体需求","品类扩展(CVD)"],"risks":["技术差距","零部件依赖","下游周期波动"],"key_q":"5nm/3nm刻蚀进展？CVD新产品进度？"},
    "688525": {"products":[("嵌入式存储eMMC/UFS","量产","手机/平板"),("SSD固态硬盘","量产","消费级/企业级"),("DRAM模组","量产","服务器/PC"),("存储卡/U盘","成熟","消费级")],"supply_chain":{"up":"三星/SK海力士/美光/长鑫(存储颗粒)","down":"联想/华为/小米/OPPO/浪潮","pos":"存储模组龙头"},"catalysts":["AI服务器→企业级SSD需求","存储周期上行","国产替代"],"risks":["存储颗粒定价权在外商","周期性波动","毛利率低"],"key_q":"企业级SSD进展？长鑫合作？AI存储需求占比？"},
    "603986": {"products":[("NOR Flash","量产","全球前三"),("MCU微控制器","量产","32位ARM"),("DRAM代销","成熟","长鑫DRAM代理"),("SLC NAND","量产","小容量存储")],"supply_chain":{"up":"中芯国际/华虹(代工)","down":"华为/小米/OPPO/比亚迪/博世","pos":"NOR Flash+MCU双龙头"},"catalysts":["NOR Flash涨价周期","MCU国产替代","长鑫IPO→DRAM受益","Q1利润14.6亿"],"risks":["NOR Flash周期性","MCU竞争激烈","朱一明减持(长鑫董事长)"],"key_q":"长鑫IPO后关系变化？自研DRAM进展？汽车MCU认证？"},
    "688008": {"products":[("DDR5内存接口芯片","量产","全球市占率领先"),("PCIe Retimer芯片","量产","AI服务器互联"),("MXC内存扩展芯片","研发中","CXL标准"),("津逮服务器CPU","量产","国产x86")],"supply_chain":{"up":"台积电(代工)","down":"三星/SK海力士/美光(内存厂)→服务器OEM","pos":"内存接口芯片全球龙头"},"catalysts":["DDR5渗透率提升","AI服务器→PCIe Retimer需求","CXL标准→MXC芯片","纳入富时A50"],"risks":["DDR5渗透趋缓","内存周期波动","Intel Sapphire Rapids延迟"],"key_q":"PCIe Retimer市占率？MXC芯片进度？DDR6预研？"},
    "002916": {"products":[("IC载板","量产","封装基板"),("高多层PCB","量产","AI服务器/交换机"),("HDI板","量产","手机/消费电子"),("背板/高速板","量产","通信设备")],"supply_chain":{"up":"生益/南亚(覆铜板)+日矿(铜箔)","down":"华为/中兴/浪潮/烽火/NVIDIA(间接)","pos":"国内IC载板+高多层PCB龙头"},"catalysts":["定增48.82亿→AI算力PCB扩产","AI服务器PCB需求爆发","IC载板国产替代"],"risks":["IC载板竞争激烈","下游需求波动","原材料涨价"],"key_q":"AI算力PCB收入占比？IC载板客户导入？定增项目进度？"},
    "002463": {"products":[("AI服务器PCB","量产","高速高多层板"),("汽车PCB","量产","ADAS/域控"),("通信PCB","量产","5G基站/交换机"),("HDI板","量产","消费电子")],"supply_chain":{"up":"生益/台光(覆铜板)","down":"华为/中兴/浪潮/思科/NVIDIA","pos":"AI服务器PCB龙头"},"catalysts":["AI服务器→高速PCB需求","股价创历史新高","汽车电子增长","融资余额大增"],"risks":["PCB行业周期性强","竞争加剧","原材料波动"],"key_q":"AI PCB收入占比？海外客户拓展？产能扩张？"},
    "688017": {"products":[("谐波减速器","量产","人形机器人核心零部件"),("精密传动部件","量产","工业机器人/机床")],"supply_chain":{"up":"钢材/轴承/密封件","down":"优必选/傅利叶/特斯拉(潜在)/ABB/发那科","pos":"国产谐波减速器龙头"},"catalysts":["人形机器人产业化(特斯拉Optimus等)","国产替代(HarmonicDrive)","专精特新政策"],"risks":["人形机器人量产不及预期","日本Harmonic竞争","价格战风险"],"key_q":"特斯拉Optimus供应链进展？产能规划？技术代差？"},
}

# 按赛道自动生成
def auto_generate(stock):
    cat = stock["category"]
    name = stock["name"]
    biz = stock.get("core_business", "")
    q1r = stock.get("q1_revenue")
    q1p = stock.get("q1_profit")

    # Build products from business description
    products = []
    for kw, prod in [("光模块","光模块"),("光器件","光器件"),("光芯片","光芯片"),
                     ("光纤","光纤/光缆"),("光缆","光纤/光缆"),("激光","激光器/设备"),
                     ("芯片","芯片"),("半导体","半导体产品"),("封测","封测服务"),
                     ("晶圆","晶圆代工"),("PCB","PCB"),("覆铜板","覆铜板"),
                     ("服务器","服务器"),("算力","算力服务"),("数据中心","数据中心"),
                     ("液冷","液冷方案"),("连接器","连接器"),("传感器","传感器"),
                     ("软件","软件平台"),("AI应用","AI应用"),("人工智能","AI产品"),
                     ("机器人","机器人产品"),("减速器","减速器"),("伺服","伺服系统"),
                     ("安全","安全产品"),("物联网","物联网方案"),("通信","通信设备"),
                     ("设备","设备产品"),("材料","材料产品"),("元器件","元器件"),
                     ("电源","电源设备"),("云","云服务")]:
        if kw in biz:
            products.append((prod, "量产", "核心产品"))
            break
    if not products:
        products.append(("主营产品", "量产", biz[:30] if biz else "待补充"))

    # Supply chain (generic by category)
    sc = {"up": "上游供应商", "down": "下游客户", "pos": "产业链参与者"}
    if cat == "optical":
        sc = {"up": "光芯片/电芯片/PCB/结构件供应商", "down": "光模块厂/设备商/互联网/运营商", "pos": "光通信产业链"}
    elif cat == "chip":
        sc = {"up": "设备/材料/EDA/IP供应商", "down": "模组厂/整机厂/终端品牌", "pos": "半导体产业链"}
    elif cat == "compute":
        sc = {"up": "GPU/CPU/内存/PCB供应商", "down": "互联网/运营商/金融/政府", "pos": "AI算力产业链"}
    elif cat == "robot":
        sc = {"up": "减速器/伺服/控制器/传感器供应商", "down": "汽车/3C/物流/医疗制造商", "pos": "机器人产业链"}
    elif cat == "app":
        sc = {"up": "云服务/芯片/数据供应商", "down": "企业/政府/消费者", "pos": "AI应用软件层"}
    elif cat == "infra":
        sc = {"up": "设备/电力/机柜供应商", "down": "互联网/运营商/金融", "pos": "AI基础设施层"}

    # Catalysts
    catalysts = []
    if q1r and q1p:
        rev_yoy = stock.get("q1_revenue_yoy", 0)
        prof_yoy = stock.get("q1_profit_yoy", 0)
        if rev_yoy > 0:
            catalysts.append(f"Q1营收+{rev_yoy:.0f}%→业绩增长")
        if prof_yoy > 0:
            catalysts.append(f"Q1利润+{prof_yoy:.0f}%→盈利改善")
    if cat == "optical": catalysts += ["AI数据中心→光通信需求", "800G/1.6T升级周期"]
    elif cat == "chip": catalysts += ["国产替代加速", "AI芯片需求爆发"]
    elif cat == "compute": catalysts += ["AI算力基建高速增长", "互联网大厂资本开支增加"]
    elif cat == "robot": catalysts += ["人形机器人产业化预期", "制造业自动化升级"]
    elif cat == "app": catalysts += ["AI应用商业化落地", "大模型技术迭代"]
    elif cat == "infra": catalysts += ["AI数据中心扩建", "算力基建政策支持"]

    # Risks
    risks = ["行业竞争加剧", "下游需求波动"]
    if cat in ("chip", "optical"):
        risks += ["核心芯片/材料依赖进口", "地缘政治风险"]
    if cat == "compute":
        risks += ["芯片供应受限", "价格战风险"]
    if q1p and q1p < 0:
        risks.append("当前亏损→盈利拐点不确定")

    # Key question
    key_q_pool = {
        "optical": "是否有自研光芯片(EML/DFB/DSP)？这是光模块公司核心壁垒",
        "chip": "制程节点？受美国制裁影响吗？客户是谁？国产替代进度？",
        "compute": "核心芯片来源(NVIDIA/华为/自研)？液冷方案？",
        "robot": "核心零部件自研率？是否进入特斯拉/华为供应链？",
        "app": "AI收入占比？是否接入DeepSeek等大模型？",
        "infra": "数据中心上架率？PUE水平？大客户是谁？",
        "other": "AI业务实质性收入占比？",
    }
    key_q = key_q_pool.get(cat, key_q_pool["other"])

    return {
        "products": products,
        "supply_chain": sc,
        "catalysts": catalysts[:5] if catalysts else ["行业趋势驱动"],
        "risks": risks[:4],
        "key_q": key_q,
    }

def main():
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    manual_count = 0
    auto_count = 0
    for stock in data["stocks"]:
        code = stock["code"]
        if code in MANUAL:
            m = MANUAL[code]
            # Convert tuple products to dict
            products = [{"name": p[0], "status": p[1], "detail": p[2]} for p in m["products"]]
            sc = {"upstream": m["supply_chain"]["up"], "downstream": m["supply_chain"]["down"], "position": m["supply_chain"]["pos"]}
            stock["deep_analysis"] = {
                "products": products,
                "supply_chain": sc,
                "catalysts": m["catalysts"],
                "risks": m["risks"],
                "key_question": m["key_q"],
            }
            manual_count += 1
        else:
            stock["deep_analysis"] = auto_generate(stock)
            auto_count += 1

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Deep analysis: {manual_count} detailed + {auto_count} auto = {data['total']}")

if __name__ == "__main__":
    main()
