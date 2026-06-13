#!/usr/bin/env python3
"""从自选股和手动映射构建完整 AI 看板数据"""
import json, os, sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
SELF_STOCKS = os.path.join(DATA_DIR, '..', '..', 'stock_data_output', 'ths_self_stocks.json')
RAW_INFO = os.path.join(DATA_DIR, '..', '..', 'SelfStockInfo.json')

# AI 核心业务与分类映射
BIZ_MAP = {
    "300308": ("高速光模块龙头(800G/1.6T)", "optical"),
    "300502": ("高速光模块(800G/LPO)", "optical"),
    "300394": ("光器件(FA/连接器)", "optical"),
    "002281": ("光模块/光器件", "optical"),
    "300620": ("光器件/调制器芯片", "optical"),
    "300548": ("PLC光分路器/AWG芯片", "optical"),
    "300570": ("光连接器/适配器", "optical"),
    "688205": ("光芯片(DSP/Driver)", "optical"),
    "688498": ("光芯片IDM(EML/DFB)", "optical"),
    "688313": ("PLC分路器芯片/光芯片", "optical"),
    "688195": ("光器件/精密光学透镜", "optical"),
    "300913": ("高速连接器/铜缆", "optical"),
    "301191": ("光器件/陶瓷基板", "optical"),
    "601869": ("光纤预制棒/光缆/海缆", "optical"),
    "600487": ("光纤光缆/海洋通信/智能电网", "optical"),
    "600522": ("光纤光缆/海缆/新能源", "optical"),
    "600345": ("光纤光缆/5G", "optical"),
    "688048": ("激光器芯片(EML/DFB)", "optical"),
    "300548": ("PLC光分路器芯片", "optical"),
    "002897": ("高速连接器", "optical"),
    "688041": ("国产AI芯片龙头(DCU/海光)", "chip"),
    "688256": ("国产AI芯片(思元/寒武纪)", "chip"),
    "688047": ("国产CPU(龙芯)", "chip"),
    "603019": ("国产算力服务器(曙光)", "compute"),
    "688008": ("内存接口芯片(澜起)", "chip"),
    "688981": ("晶圆代工龙头(中芯国际)", "chip"),
    "002371": ("半导体设备龙头(北方华创)", "chip"),
    "600584": ("半导体封测龙头(长电)", "chip"),
    "002156": ("半导体封测(通富微电)", "chip"),
    "002463": ("AI服务器PCB龙头(沪电)", "chip"),
    "002916": ("IC载板/PCB(深南电路)", "chip"),
    "002938": ("HDI/类载板(鹏鼎)", "chip"),
    "688525": ("存储芯片/模组(佰维)", "chip"),
    "688766": ("NOR Flash(普冉)", "chip"),
    "688629": ("高速连接器(华丰)", "infra"),
    "601138": ("AI服务器/云计算(工业富联)", "compute"),
    "600183": ("覆铜板/PCB材料(生益)", "chip"),
    "002384": ("PCB/精密制造(东山精密)", "chip"),
    "600330": ("磁性材料/蓝宝石", "chip"),
    "600667": ("半导体/工程EPC(太极)", "chip"),
    "601126": ("智能电网/新能源", "other"),
    "601208": ("绝缘材料/光学膜", "other"),
    "603063": ("电源设备/新能源", "infra"),
    "603083": ("通信设备/光器件", "optical"),
    "603256": ("精密结构件", "other"),
    "603459": ("精密结构件/新能源汽车", "other"),
    "603629": ("精密结构件/汽车零部件", "other"),
    "603678": ("MLCC陶瓷电容", "chip"),
    "603773": ("光学玻璃/光掩模基板", "optical"),
    "603986": ("NOR Flash/MCU(兆易创新)", "chip"),
    "688012": ("半导体设备(中微)", "chip"),
    "688017": ("谐波减速器(绿的谐波)", "robot"),
    "688120": ("半导体设备(CMP)", "chip"),
    "688143": ("特种光纤/光纤器件", "optical"),
    "688170": ("半导体设备(检测)", "chip"),
    "688220": ("蜂窝通信芯片", "chip"),
}

def main():
    # 加载自选股列表
    with open(SELF_STOCKS, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    # 加载原始价格数据
    prices = {}
    if os.path.exists(RAW_INFO):
        with open(RAW_INFO, 'r', encoding='utf-8') as f:
            raw_prices = json.load(f)
        for item in raw_prices:
            p_val = item.get('P', '')
            prices[item.get('C', '')] = float(p_val) if p_val and p_val != '' else 0

    stocks = []
    for s in raw:
        code = s['code']
        biz, cat = BIZ_MAP.get(code, ('', 'other'))
        price = prices.get(code, 0)

        stock = {
            "code": code,
            "name": s['name'],
            "market": "sh" if code.startswith('6') else "sz",
            "core_business": biz,
            "category": cat,
            "price": price,
            "change_pct": 0,
            "market_cap": 0,
            "pe": 0,
            "pb": 0,
            "concepts": [],
            "latest_news": [],
            "revenue_detail": "",
            "added_price": s.get('added_price', 0),
            "added_date": s.get('added_date', ''),
        }
        stocks.append(stock)

    # 写 universe.json
    universe = {
        "updated": "2026-06-13T15:30:00+08:00",
        "total": len(stocks),
        "stocks": stocks
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, 'universe.json'), 'w', encoding='utf-8') as f:
        json.dump(universe, f, ensure_ascii=False, indent=2)

    # 统计分类
    cat_counts = {}
    for s in stocks:
        cat_counts[s['category']] = cat_counts.get(s['category'], 0) + 1

    with open(os.path.join(DATA_DIR, 'universe.json'), 'r', encoding='utf-8') as f:
        _ = json.load(f)

    print(f'OK: {len(stocks)} stocks, categories: {cat_counts}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
