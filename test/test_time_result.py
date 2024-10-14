import asyncio
import json
import time

# Helper function to send a query to the indexing server
async def query_indexing_server(topic):
    reader, writer = await asyncio.open_connection("localhost", 6000)
    command = json.dumps({"command": "query_topic", "topic": topic})
    writer.write(command.encode())
    await writer.drain()
    response = await reader.read(1024)
    writer.close()
    await writer.wait_closed()
    return json.loads(response.decode())

async def measure_query_time(peer_port, topic):
    start_time = time.time()
    response = await query_indexing_server(topic)
    end_time = time.time()
    query_time = end_time - start_time
    print(f"Query Time for Peer {peer_port}: {query_time:.5f} seconds")
    return query_time

async def run_query_tests():
    total_time = 0
    num_requests = 1000
    
    for _ in range(num_requests):
        query_time = await measure_query_time(5555, "Games")
        total_time += query_time
    
    avg_time = total_time / num_requests
    print(f"Average Query Time for 1000 requests: {avg_time:.5f} seconds")

if __name__ == "__main__":
    asyncio.run(run_query_tests())
