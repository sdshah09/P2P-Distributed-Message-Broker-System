import asyncio
import json
import pytest

# Helper function to simulate the sending of a message
async def send_command(host, port, command):
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(command.encode())
    await writer.drain()
    response = await reader.read(1024)
    writer.close()
    await writer.wait_closed()
    return response.decode()

# Create topic on Peer 1
async def test_create_topic():
    command = json.dumps({"command": "create_topic", "topic": "Sports"})
    response = await send_command("localhost", 5555, command)
    response_data = json.loads(response)
    # assert response_data['status'] == 'success'
    # assert response_data['message'] == "Topic 'Sports' created"

# Subscribe Peer 2 to topic "Sports"
async def test_subscribe_peer2():
    command = json.dumps({"command": "subscribe", "topic": "Sports"})
    response = await send_command("localhost", 5556, command)
    response_data = json.loads(response)
    print(f"Response data in 2 {response_data}")
    # assert response_data['status'] == 'success'
    # assert 'Subscribed to topic' in response_data['message']

# Subscribe Peer 3 to topic "Sports"
async def test_subscribe_peer3():
    command = json.dumps({"command": "subscribe", "topic": "Sports"})
    response = await send_command("localhost", 5557, command)
    response_data = json.loads(response)
    # assert response_data['status'] == 'success'
    # assert 'Subscribed to topic' in response_data['message']
    
async def test_subscribe_peer4():
    command = json.dumps({"command": "subscribe", "topic": "Sports"})
    response = await send_command("localhost", 5558, command)
    response_data = json.loads(response)

# Publish message on Peer 1 and expect it to be forwarded to Peer 2 and Peer 3
async def test_publish_message():
    command = json.dumps({"command": "publish", "topic": "Sports", "message": "Football match tonight!"})
    response = await send_command("localhost", 5555, command)
    response_data = json.loads(response)
    # assert response_data['status'] == 'success'
    # assert response_data['message'] == "Message published on topic 'Sports'"

# Pull messages on Peer 2 and Peer 3 to check if they received the message
# async def test_pull_peer2():
#     command = json.dumps({"command": "pull", "topic": "Sports"})
#     response = await send_command("localhost", 5556, command)
#     response_data = json.loads(response)
#     print(f"Response from Peer 2: {response}")  # Debug print

#     # assert response_data['status'] == 'success'
#     # assert "Football match tonight!" in response_data['messages']

# async def test_pull_peer3():
#     command = json.dumps({"command": "pull", "topic": "Sports"})
#     response = await send_command("localhost", 5557, command)
#     response_data = json.loads(response)
#     # assert response_data['status'] == 'success'
#     # assert "Football match tonight!" in response_data['messages']


# The main test runner to test all functions
@pytest.mark.asyncio
async def test_subscribe_and_publish():
    # Step 1: Create topic on Peer 1
    await test_create_topic()

    # Step 2: Subscribe Peer 2 and Peer 3 to topic "Sports"
    await test_subscribe_peer2()
    await test_subscribe_peer3()
    await test_subscribe_peer4()
    # Step 3: Publish a message from Peer 1
    await test_publish_message()

    # Step 4: Pull and verify messages on Peer 2 and Peer 3
    # await test_pull_peer2()
    # await test_pull_peer3()

# Run the test using asyncio event loop
if __name__ == "__main__":
    asyncio.run(test_subscribe_and_publish())
