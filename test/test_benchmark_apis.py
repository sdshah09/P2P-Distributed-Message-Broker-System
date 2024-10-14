import asyncio
import json
import time

# Helper function to send a command to a peer
async def send_command(host, port, command):
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(command.encode())
    await writer.drain()
    response = await reader.read(1024)
    writer.close()
    await writer.wait_closed()
    return json.loads(response.decode())

async def benchmark_latency(api_function, num_requests):
    total_time = 0
    for _ in range(num_requests):
        start_time = time.time()
        await api_function()
        end_time = time.time()
        total_time += (end_time - start_time)
    
    avg_latency = total_time / num_requests
    print(f"Average Latency for {api_function.__name__}: {avg_latency:.5f} seconds")

async def benchmark_throughput(api_function, num_requests):
    start_time = time.time()
    for _ in range(num_requests):
        await api_function()
    end_time = time.time()
    
    throughput = num_requests / (end_time - start_time)
    print(f"Throughput for {api_function.__name__}: {throughput:.2f} requests/second")

# Test create topic
async def create_topic():
    command = json.dumps({"command": "create_topic", "topic": "Sports"})
    await send_command("localhost", 5555, command)

# Test subscribe to a topic
async def subscribe_peer():
    command = json.dumps({"command": "subscribe", "topic": "Sports"})
    await send_command("localhost", 5556, command)

# Test publish message
async def publish_message():
    command = json.dumps({"command": "publish", "topic": "Sports", "message": "Football match tonight!"})
    await send_command("localhost", 5555, command)

async def run_benchmarks():
    num_requests = 1000
    
    # Benchmark Latency
    await benchmark_latency(create_topic, num_requests)
    await benchmark_latency(subscribe_peer, num_requests)
    await benchmark_latency(publish_message, num_requests)
    
    # Benchmark Throughput
    await benchmark_throughput(create_topic, num_requests)
    await benchmark_throughput(subscribe_peer, num_requests)
    await benchmark_throughput(publish_message, num_requests)

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
