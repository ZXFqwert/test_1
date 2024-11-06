import pandas as pd
import networkx as nx
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value,LpStatus
import re  # 导入正则表达式模块

# 加载超市需求数据
supermarket_data = {
    'Z1': {'employees': 68},
    'Z2': {'employees': 60},
    'Z3': {'employees': 38},
    'Z4': {'employees': 60},
    'Z5': {'employees': 90},
    'Z6': {'employees': 60},
    'Z7': {'employees': 38},
    'Z8': {'employees': 90},
    'Z9': {'employees': 60},
}

# 加载仓库容量数据
warehouse_data = {
    'C1': {'capacity': 600},
    'C2': {'capacity': 800},
    'C3': {'capacity': 800},
    'C4': {'capacity': 800},
    'C5': {'capacity': 800},
    'C6': {'capacity': 800},
    'C7': {'capacity': 600},
    'C8': {'capacity': 800},
    'C9': {'capacity': 500},
}

# 计算每个超市的日需求量
for supermarket, data in supermarket_data.items():
    employees = data['employees']
    data['daily_food'] = employees * 5  # 食品
    data['daily_water'] = employees * 2.5  # 水
    data['daily_total'] = data['daily_food'] + data['daily_water']  # 总需求

# 定义路径和权重
paths = [
    ('C1', 'Z1', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C1', 'Z2', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C2', 'Z2', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C2', 'Z3', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C3', 'Z3', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C3', 'Z4', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C4', 'Z4', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C4', 'Z5', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C5', 'Z5', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C5', 'Z6', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C6', 'Z6', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C6', 'Z7', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C7', 'Z7', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C7', 'Z8', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C8', 'Z8', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C8', 'Z9', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
    ('C9', 'Z9', {'weight1': 1, 'weight2': 1, 'weight3': 1}),
]

# 创建图
G = nx.Graph()
G.add_edges_from(paths)

# 定义优化模型
model = LpProblem("Supermarket_Supply_Optimization", LpMinimize)

# 定义变量
truck_variables = LpVariable.dicts("Truck",
                                   [(c, s, t) for c in warehouse_data.keys() for s in supermarket_data.keys() for t in
                                    range(15 * 24)], 0, None, cat='Continuous')
storage_variables = LpVariable.dicts("Storage", [(s, t) for s in supermarket_data.keys() for t in range(15 * 24)], 0,
                                     None, cat='Continuous')

# 目标函数：最小化使用的货车数量
model += lpSum(truck_variables)

# 约束条件
for supermarket, data in supermarket_data.items():
    daily_total = data['daily_total']
    max_storage = daily_total * 3.5
    min_storage = daily_total * 0.25
    initial_storage = daily_total * 2

    # 初始库存
    model += storage_variables[(supermarket, 0)] == initial_storage

    for t in range(1, 15 * 24):
        # 库存更新
        model += storage_variables[(supermarket, t)] == storage_variables[
            (supermarket, t - 1)] - daily_total / 24 + lpSum(
            truck_variables[(c, supermarket, t)] * warehouse_data[c]['capacity'] for c in warehouse_data.keys())

        # 库存限制
        model += storage_variables[(supermarket, t)] <= max_storage
        model += storage_variables[(supermarket, t)] >= min_storage

# 解决模型
model.solve()

# 输出结果
print(f"Status: {LpStatus[model.status]}")
for v in model.variables():
    if v.varValue > 0:
        print(f"{v.name} = {v.varValue}")


# 生成15天内各超市的物资持有量变化情况
results = {}
for supermarket in supermarket_data.keys():
    storage_over_time = [value(storage_variables[(supermarket, t)]) for t in range(15 * 24)]
    results[supermarket] = storage_over_time

# 将结果保存到Excel文件
result_df = pd.DataFrame(results)
result_df.to_excel('Result2.xlsx', index=False)

# 生成货车运行日志
trucks_log = []
for v in model.variables():
    if v.varValue > 0 and v.name.startswith('Truck'):
        match = re.match(r'Truck_(\w+)_(\w+)_(\d+)', v.name)
        if match:
            c, s, t = match.groups()
            t = int(t)
            trucks_log.append({
                'Truck': v.name,
                'Start_Warehouse': c,
                'End_Supermarket': s,
                'Quantity': v.varValue * warehouse_data[c]['capacity'],
                'Start_Time': t,
                'End_Time': t + 72  # 假设每次运输时间为3天
            })

trucks_log_df = pd.DataFrame(trucks_log)
trucks_log_df.to_excel('Trucks_Log.xlsx', index=False)