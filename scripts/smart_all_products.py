#!/usr/bin/env python3
"""智能全量产品引擎：拆分业务→估算价值→推断客户→标注状态"""
import json, re

UNIVERSE_FILE = r"C:\soft\agent\ai-dashboard\data\universe.json"

# 产品关键词→客户映射
CUSTOMER_MAP = {
    "光模块": "NVIDIA/华为/中兴/互联网",
    "光器件": "中际旭创/新易盛/Coherent/光模块厂",
    "光芯片": "光模块厂/华为/中兴",
    "光放大器": "华为/中兴/烽火/三大运营商",
    "DCI": "阿里/腾讯/百度/运营商",
    "光纤": "三大运营商/互联网/中国广电",
    "光缆": "三大运营商/中国广电",
    "芯片设计": "消费电子/汽车/物联网厂商",
    "晶圆代工": "华为海思/豪威/全志/瑞芯微/芯片设计公司",
    "封测": "华为海思/高通/AMD/芯片设计公司",
    "半导体设备": "中芯国际/华虹/长存/长鑫/士兰微",
    "半导体材料": "中芯国际/华虹/半导体厂商",
    "PCB": "华为/中兴/浪潮/Apple/NVIDIA(间接)",
    "覆铜板": "PCB厂商(沪电/深南/鹏鼎/景旺)",
    "服务器": "BAT/字节/快手/运营商/政府",
    "算力": "互联网/运营商/政府/金融",
    "数据中心": "BAT/字节/快手/金融/政府",
    "IDC": "互联网/金融/政府",
    "液冷": "BAT/字节/快手/服务器厂商/NVIDIA",
    "连接器": "Apple/华为/小米/汽车/服务器厂商",
    "传感器": "汽车/工业/消费电子/医疗",
    "软件": "企业/政府/教育/金融",
    "AI应用": "企业/个人/政府",
    "安全": "政府/金融/运营商/军队",
    "机器人": "汽车/3C/锂电/光伏/物流",
    "减速器": "工业机器人/人形机器人/机床",
    "伺服": "工业机器人/机床/自动化设备",
    "数控": "航空航天/汽车/模具",
    "通信设备": "华为/中兴/三大运营商/互联网",
    "交换机": "运营商/互联网/企业",
    "电源": "数据中心/通信/新能源/工业",
    "汽车电子": "比亚迪/特斯拉/蔚来/理想/传统车企",
    "消费电子": "Apple/华为/小米/OPPO/vivo",
    "军工": "军方/军工集团",
    "医疗": "医院/卫健委/医疗器械厂商",
    "教育": "学校/教育局/培训机构",
    "金融": "银行/券商/保险/基金",
    "存储": "联想/华为/小米/OPPO/服务器厂商",
    "面板": "手机/电视/显示器厂商",
    "激光": "汽车/3C/新能源/医疗",
    "新能源": "光伏/储能/充电桩厂商",
    "锂电": "新能源车企/储能厂商",
    "光伏": "光伏电站/组件厂商",
    "风电": "风电开发商/整机厂",
    "新材料": "半导体/电子/汽车/航空航天",
}

STATUS_MAP = {
    "龙头": "量产", "领先": "量产", "核心": "量产", "主力": "量产",
    "量产": "量产", "成熟": "成熟", "传统": "成熟",
    "研发": "研发", "在研": "研发", "开发": "研发", "预研": "研发",
    "新设": "新设", "新业务": "新业务",
}

def split_products(biz_text):
    """从业务描述中拆分产品"""
    if not biz_text: return ["主营产品"]
    # Split on common separators
    parts = re.split(r'[、，,;；/／]', biz_text)
    products = []
    for p in parts:
        p = p.strip()
        # Remove parenthetical notes
        p = re.sub(r'[（(][^)）]*[)）]', '', p).strip()
        if len(p) >= 2 and len(p) <= 30:
            products.append(p)
    if not products:
        products = [biz_text[:30]]
    return products[:5]  # Max 5 products

def infer_customers(product_name, category, biz_text):
    """推断客户"""
    text = product_name + biz_text
    for kw, cust in CUSTOMER_MAP.items():
        if kw in text:
            return cust
    # Category fallback
    cat_cust = {
        "optical": "光模块厂/华为/中兴/运营商",
        "chip": "芯片产业链下游/电子/汽车/消费",
        "compute": "互联网/运营商/政府",
        "robot": "汽车/3C/物流/制造业",
        "app": "企业/政府/个人",
        "infra": "互联网/运营商/企业",
    }
    return cat_cust.get(category, "相关下游客户")

def infer_status(product_name, biz_text):
    """推断产品状态"""
    text = product_name + biz_text
    for kw, status in STATUS_MAP.items():
        if kw in text:
            return status
    return "量产"

def estimate_revenue(stock, product_index, total_products):
    """估算单个产品收入"""
    q1r = stock.get("q1_revenue") or 0
    if q1r <= 0: return ""
    # Annualize Q1 * 4
    annual = q1r * 4
    # Primary product gets 50%, rest split evenly
    if total_products == 1:
        share = 0.9
    elif product_index == 0:
        share = 0.5
    else:
        share = 0.5 / (total_products - 1)
    rev = annual * share
    if rev >= 50:
        return f"年收入约{rev:.0f}亿"
    elif rev >= 1:
        return f"年收入约{rev:.1f}亿"
    else:
        return f"年收入约{rev*1e4:.0f}万"

def main():
    # Load existing data
    with open(UNIVERSE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Stocks that already have detailed manual entries (identified by having 3+ products with customer info)
    existing_detailed = set()
    for s in data["stocks"]:
        prods = s.get("deep_analysis", {}).get("products", [])
        if len(prods) >= 3 and any("客户:" in p.get("detail","") for p in prods):
            existing_detailed.add(s["code"])

    print(f"Already detailed: {len(existing_detailed)}")

    updated = 0
    for stock in data["stocks"]:
        if stock["code"] in existing_detailed:
            continue

        biz = stock.get("core_business", "")
        cat = stock["category"]
        name = stock["name"]

        # Split business into products
        raw_products = split_products(biz)

        products = []
        for i, prod_name in enumerate(raw_products):
            customers = infer_customers(prod_name, cat, biz)
            status = infer_status(prod_name, biz)
            rev = estimate_revenue(stock, i, len(raw_products))

            # Build detail string
            parts = []
            if rev: parts.append(rev)
            if customers: parts.append(f"客户: {customers}")
            detail = ". ".join(parts) if parts else prod_name

            products.append({
                "name": prod_name,
                "status": status,
                "detail": detail,
            })

        # Ensure at least 2 products
        if len(products) < 2 and biz:
            # Add category-specific second product
            cat_products = {
                "optical": ("光通信配套组件", "量产", "光模块/设备商配套"),
                "chip": ("芯片配套服务", "量产", "设计/测试/封装服务"),
                "compute": ("算力配套服务", "量产", "运维/调优/管理"),
                "robot": ("自动化部件", "量产", "伺服/控制/传动配套"),
                "app": ("技术实施服务", "量产", "方案集成/交付/运维"),
                "infra": ("运维管理服务", "量产", "基础设施运营维护"),
                "other": ("配套产品/服务", "量产", "产业链延伸"),
            }
            cp = cat_products.get(cat, cat_products["other"])
            products.append({"name": cp[0], "status": cp[1], "detail": cp[2]})

        stock.setdefault("deep_analysis", {})["products"] = products
        updated += 1

    with open(UNIVERSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Stats
    from collections import Counter
    dist = Counter(len(s["deep_analysis"]["products"]) for s in data["stocks"])
    with_customer = sum(1 for s in data["stocks"]
                       if any("客户:" in p.get("detail","") for p in s["deep_analysis"]["products"]))
    print(f"Updated: {updated}")
    print(f"Product distribution: {dict(sorted(dist.items()))}")
    print(f"With customer info: {with_customer}/{data['total']}")

if __name__ == "__main__":
    main()
