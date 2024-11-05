import random
import matplotlib.pyplot as plt

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.state = 'idle'
        self.send_time = None
        self.frame_length = None
        self.retransmit_count = 0
        self.K = None

def is_channel_idle(channel, current_time, propagation_delay):
    for entry in channel:
        if entry[1] + propagation_delay <= current_time:
            return False
    return True

def detect_collision(channel, node_id, current_time, propagation_delay):
    for entry in channel:
        if entry[0] != node_id and entry[1] + propagation_delay <= current_time:
            return True
    return False

def simulate_csma_cd(p, propagation_delay, t_trans, num_nodes=10, simulation_time=1000, time_step=0.1):
    nodes = [Node(i) for i in range(num_nodes)]
    channel = []
    sum_success = 0
    current_time = 0

    while current_time < simulation_time:
        for node in nodes:
            if node.state == 'idle':
                if random.random() < p:
                    node.frame_length = t_trans
                    if is_channel_idle(channel, current_time, propagation_delay):
                        node.state = 'sending'
                        node.send_time = current_time
                        channel.append([node.node_id, node.send_time, node.frame_length])
            elif node.state == 'sending':
                if detect_collision(channel, node.node_id, current_time, propagation_delay):
                    # 发生碰撞
                    node.state = 'retransmit_wait'
                    node.retransmit_count += 1
                    backoff_time = random.choice(range(2 ** min(10, node.retransmit_count))) * 2 * propagation_delay
                    node.K = current_time + backoff_time
                    channel.remove([node.node_id, node.send_time, node.frame_length])
                    channel.append([node.node_id, current_time, 0])
                elif current_time >= node.send_time + node.frame_length + propagation_delay:
                    # 成功发送
                    sum_success += node.frame_length
                    node.state = 'idle'
                    channel.remove([node.node_id, node.send_time, node.frame_length])
                    node.retransmit_count = 0
                    node.K = None
                    node.send_time = None
                    node.frame_length = None
            elif node.state == 'retransmit_wait':
                if node.K <= current_time and is_channel_idle(channel, current_time, propagation_delay):
                    node.state = 'sending'
                    node.send_time = current_time
                    node.frame_length = t_trans
                    channel.append([node.node_id, node.send_time, node.frame_length])

        # 清理已完成的传输记录
        channel = [entry for entry in channel if entry[1] + entry[2] + propagation_delay > current_time]

        current_time += time_step

    return sum_success / simulation_time

# 参数设置
p = 0.1  # 每个时间步生成帧的概率
t_trans = 10  # 帧传输时间

# 计算不同 propagation_delay 下的效率
propagation_delays = [i * 0.2 for i in range(1, 26)]  # 从0.2到5
efficiencies = []

for propagation_delay in propagation_delays:
    efficiency = simulate_csma_cd(p, propagation_delay, t_trans)
    efficiencies.append(efficiency)

# 绘制图形
plt.figure(figsize=(10, 6))
plt.plot(propagation_delays, efficiencies, label='Simulated Efficiency')
plt.plot(propagation_delays, [1 / (1 + 5 * pd / t_trans) for pd in propagation_delays], label='Theoretical Efficiency', linestyle='--')
plt.xlabel('Propagation Delay(t_prop)')
plt.ylabel('Efficiency')
plt.title('Efficiency vs Propagation Delay Time(t_prop)')
plt.legend()
plt.grid(True)
plt.show()

# 打印理论效率
print(1 / (1 + 5 * 1 / 8))