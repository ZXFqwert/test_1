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
propagation_delay = 1  # 假设传播时延为1秒

# 计算不同 t_trans 下的效率
t_trans_values = range(2, 21)
efficiencies = []

for t_trans in t_trans_values:
    efficiency = simulate_csma_cd(p, propagation_delay, t_trans)
    efficiencies.append(efficiency)

# 绘制图形
plt.figure(figsize=(10, 6))
plt.plot(t_trans_values, efficiencies, label='Simulated Efficiency')
plt.plot(t_trans_values, [1 / (1 + 5 * propagation_delay / t) for t in t_trans_values], label='Theoretical Efficiency', linestyle='--')
plt.xlabel('Frame Transmission Time (t_trans)')
plt.ylabel('Efficiency')
plt.title('Efficiency vs Frame Transmission Time (t_trans)')
plt.legend()
plt.grid(True)
plt.show()

# 打印理论效率
print(1 / (1 + 5 * propagation_delay / 8))

