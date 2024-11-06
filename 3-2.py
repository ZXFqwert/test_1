import pandas as pd
from datetime import timedelta, datetime

# 定义路径消耗
paths = {
    ('H', 'C1'): {'time': 0.9, 'power': 9},
    ('H', 'C2'): {'time': 1.4, 'power': 13},
    ('H', 'C3'): {'time': 1.1, 'power': 10},
    ('H', 'C4'): {'time': 1.0, 'power': 9},
    ('H', 'C5'): {'time': 1.3, 'power': 13},
    ('H', 'C6'): {'time': 2.2, 'power': 23},
    ('H', 'C7'): {'time': 2.5, 'power': 25},
    ('H', 'C8'): {'time': 2.7, 'power': 28},
    ('H', 'C9'): {'time': 3.2, 'power': 31},
    ('C1', 'Z1'): {'time': 2.2, 'power': 45},
    ('C1', 'Z2'): {'time': 1.9, 'power': 40},
    ('C2', 'Z2'): {'time': 1.0, 'power': 26},
    ('C2', 'Z3'): {'time': 1.3, 'power': 34},
    ('C3', 'Z3'): {'time': 1.8, 'power': 38},
    ('C3', 'Z4'): {'time': 2.0, 'power': 50},
    ('C4', 'Z4'): {'time': 1.7, 'power': 39},
    ('C4', 'Z5'): {'time': 2.1, 'power': 50},
    ('C5', 'Z5'): {'time': 2.3, 'power': 42},
    ('C5', 'Z6'): {'time': 2.2, 'power': 42},
    ('C6', 'Z6'): {'time': 0.8, 'power': 21},
    ('C6', 'Z7'): {'time': 0.9, 'power': 23},
    ('C7', 'Z7'): {'time': 1, 'power': 25},
    ('C7', 'Z8'): {'time': 1.2, 'power': 30},
    ('C8', 'Z8'): {'time': 1.1, 'power': 28},
    ('C8', 'Z9'): {'time': 1.8, 'power': 37},
    ('C9', 'Z9'): {'time': 0.8, 'power': 21},
}

# 每日需求量
daily_demand = [510, 450, 285, 450, 675, 450, 285, 675, 450]

# 车辆信息
vehicles = {
    'A': {'count': 4, 'capacity': 500, 'charge_time': {0: 8, 20: 6, 50: 4, 80: 2}, 'initial_charge': 100},
    'B': {'count': 2, 'capacity': 1000}
}

# 中转仓库
warehouses = ['C1', 'C6', 'C8']


# 生成日志
def generate_log(days=15):
    logs = []
    current_time = datetime(2024, 10, 15, 0, 0)

    # 计算15天内的总需求
    total_demand = [d * days for d in daily_demand]

    # B车运输
    b_cargo = 0
    for i in range(len(warehouses)):
        while total_demand[i] > 0:
            if b_cargo < vehicles['B']['capacity']:
                # 装货
                load_time = 1
                logs.append(
                    [current_time, f'B{i + 1}', 'H', '装载', min(vehicles['B']['capacity'] - b_cargo, total_demand[i]),
                     load_time])
                current_time += timedelta(hours=load_time)
                b_cargo += min(vehicles['B']['capacity'] - b_cargo, total_demand[i])

            # 运输
            transport_time = paths[('H', warehouses[i])]['time']
            logs.append([current_time, f'B{i + 1}', 'H', '行驶', warehouses[i], transport_time])
            current_time += timedelta(hours=transport_time)

            # 卸货
            unload_time = 1
            logs.append([current_time, f'B{i + 1}', warehouses[i], '卸载', b_cargo, unload_time])
            current_time += timedelta(hours=unload_time)
            total_demand[i] -= b_cargo
            b_cargo = 0

    # A车运输
    for i in range(vehicles['A']['count']):
        a_cargo = 0
        a_charge = vehicles['A']['initial_charge']
        for j in range(len(warehouses)):
            while total_demand[j] > 0:
                if a_cargo < vehicles['A']['capacity']:
                    # 装货
                    load_time = 0.5
                    logs.append([current_time, f'A{i + 1}', warehouses[j], '装载',
                                 min(vehicles['A']['capacity'] - a_cargo, total_demand[j]), load_time])
                    current_time += timedelta(hours=load_time)
                    a_cargo += min(vehicles['A']['capacity'] - a_cargo, total_demand[j])

                # 充电
                if a_charge < 20:
                    charge_time = vehicles['A']['charge_time'][0]
                elif 20 <= a_charge < 50:
                    charge_time = vehicles['A']['charge_time'][20]
                elif 50 <= a_charge < 80:
                    charge_time = vehicles['A']['charge_time'][50]
                else:
                    charge_time = vehicles['A']['charge_time'][80]
                a_charge = 100
                logs.append([current_time, f'A{i + 1}', warehouses[j], '充电', a_charge, charge_time])
                current_time += timedelta(hours=charge_time)

                # 运输
                transport_time = paths[(warehouses[j], f'Z{j + 1}')]['time']
                a_charge -= paths[(warehouses[j], f'Z{j + 1}')]['power']
                logs.append([current_time, f'A{i + 1}', warehouses[j], '行驶', f'Z{j + 1}', transport_time])
                current_time += timedelta(hours=transport_time)

                # 卸货
                unload_time = 0.5
                logs.append([current_time, f'A{i + 1}', f'Z{j + 1}', '卸载', a_cargo, unload_time])
                current_time += timedelta(hours=unload_time)
                total_demand[j] -= a_cargo
                a_cargo = 0

    # 保存日志到Excel
    df = pd.DataFrame(logs, columns=['时刻（小时）', '车辆ID', '点位', '状态', '参数', '耗时（小时）'])
    df.to_excel('vehicle_log.xlsx', index=False)


generate_log()