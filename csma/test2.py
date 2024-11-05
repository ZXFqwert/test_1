import random
import matplotlib.pyplot as plt

class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.success_count = 0
        self.failure_count = 0

    def attempt_send(self, p):
        if random.random() < p:
            return True
        return False

class Network:
    def __init__(self, num_nodes, p, T):
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.p = p
        self.T = T

    def simulate(self):
        for _ in range(self.T):
            sending_nodes = [node for node in self.nodes if node.attempt_send(self.p)]
            if len(sending_nodes) > 1:
                for node in sending_nodes:
                    node.failure_count += 1
            else:
                for node in sending_nodes:
                    node.success_count += 1

    def calculate_efficiency(self):
        total_attempts = self.T
        total_successes = sum(node.success_count for node in self.nodes)
        return total_successes / total_attempts if total_attempts > 0 else 0

def plot_efficiency():
    plt.figure(figsize=(10, 6))
    probabilities = [0.1, 0.05, 0.025]
    for p in probabilities:
        efficiencies = []
        for num_nodes in range(1, 60):
            network = Network(num_nodes, p, 2000)
            network.simulate()
            efficiency = network.calculate_efficiency()
            efficiencies.append(efficiency)
        plt.plot(range(1, 60), efficiencies, label=f'p={p}')
    plt.xlabel('Number of Nodes')
    plt.ylabel('Efficiency')
    plt.title('Efficiency vs Number of Nodes for Different Probabilities')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    plot_efficiency()