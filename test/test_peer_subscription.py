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

async def test_create_topic():
    command = json.dumps({"command": "create_topic", "topic": "Sports"})
    response = await send_command("localhost", 5555, command)
    print(f"Create Topic Response: {response}")

async def test_subscribe_peer(peer_port):
    command = json.dumps({"command": "subscribe", "topic": "Sports"})
    response = await send_command("localhost", peer_port, command)
    print(f"Subscribe Peer {peer_port} Response: {response}")

async def test_publish_message():
    command = json.dumps({"command": "publish", "topic": "Sports", "message": "Football match tonight!"})
    response = await send_command("localhost", 5555, command)
    print(f"Publish Message Response: {response}")

async def test_pull(peer_port):
    command = json.dumps({"command": "pull", "topic": "Sports"})
    response = await send_command("localhost", peer_port, command)
    print(f"Pull Messages for Peer {peer_port}: {response}")

async def test_delete_topic():
    command = json.dumps({"command": "delete_topic", "topic": "Sports"})
    response = await send_command("localhost", 5555, command)
    print(f"Delete Topic Response: {response}")

async def run_tests():
    # Test create topic
    await test_create_topic()
    await asyncio.sleep(1)

    # Test subscriptions for peer 5556 and 5557
    await test_subscribe_peer(5556)
    await test_subscribe_peer(5557)
    await test_subscribe_peer(5558)

    await asyncio.sleep(1)

    # Test publishing a message
    await test_publish_message()
    await asyncio.sleep(1)

    # Test pulling messages from peer 5556 and 5557
    # await test_pull(5556)
    # await test_pull(5557)
    # await asyncio.sleep(1)

    # Test deleting the topic
    await test_delete_topic()

if __name__ == "__main__":
    asyncio.run(run_tests())
