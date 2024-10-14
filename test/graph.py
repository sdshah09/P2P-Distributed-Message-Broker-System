import matplotlib.pyplot as plt

# Data for Latency and Throughput
api_types = ["create_topic", "subscribe_peer", "publish_message"]
latencies = [0.00185, 0.00783, 0.01350]
throughputs = [418.07, 88.18, 44.62]

# Plotting Latency and Throughput
plt.figure(figsize=(10, 5))

# Subplot for Latency
plt.subplot(1, 2, 1)
plt.bar(api_types, latencies, color='skyblue')
plt.title('API Latency')
plt.xlabel('API Type')
plt.ylabel('Latency (seconds)')

# Subplot for Throughput
plt.subplot(1, 2, 2)
plt.bar(api_types, throughputs, color='lightgreen')
plt.title('API Throughput')
plt.xlabel('API Type')
plt.ylabel('Throughput (requests/second)')

# Show the graph
plt.tight_layout()
plt.show()
