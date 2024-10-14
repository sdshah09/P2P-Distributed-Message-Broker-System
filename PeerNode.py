import argparse
import asyncio
import json
from datetime import datetime
import socket


class PeerNode:
    def __init__(self, host='localhost', port=5555, indexing_server_host='localhost', indexing_server_port=6000):
        self.host = host
        self.port = port
        self.indexing_server_host = indexing_server_host
        self.indexing_server_port = indexing_server_port
        self.topics = {}  # Store topics and messages
        self.subscribers = {}  # Store which peers have subscribed to which topics
        self.running = True
        self.log_file = f"peer_node_{port}.log"  # Log events

    async def start(self):
        # Start listening for connections
        server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        print(f"Peer node running on {self.host}:{self.port}")
        self.log_event("Peer node started.")

        # Register with indexing server
        await self.register_with_indexing_server()

        # Start accepting connections
        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Connected by {addr}")
        self.log_event(f"Connected by {addr}")

        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received: {message}")
            self.log_event(f"Received message from {addr}: {message}")

            # Process the request and send a response
            response = await self.process_request(message)
            writer.write(response.encode())
            await writer.drain()

        writer.close()
        await writer.wait_closed()

    async def process_request(self, message):
        try:
            request = json.loads(message)
            command = request.get('command')
            if command == "create_topic":
                topic = request.get('topic')
                return await self.create_topic(topic)
            elif command == "delete_topic":
                topic = request.get('topic')
                return await self.delete_topic(topic)
            elif command == "publish":
                print(f"Topic is : {request.get('topic')}")
                topic = request.get('topic')
                msg = request.get('message')
                print(msg)
                return await self.publish(topic, msg)
            elif command == "subscribe":
                topic = request.get('topic')
                return await self.subscribe(topic)
            elif command == "subscribe_to_peer":
                topic = request.get('topic')
                subscriber_port = request.get('subscriber_port')  # Get the subscriber's port
                return await self.handle_subscription(topic, subscriber_port)  # Handle the subscription
            elif command == "pull":
                topic = request.get('topic')
                return await self.pull(topic)
            elif command == "receive_message":  # Add this block to handle receive_message
                topic = request.get('topic')
                message = request.get('message')
                # Handle the received message
                self.log_event(f"Received message on topic '{topic}': {message}")
                return json.dumps({"status": "success", "message": f"Message '{message}' received on topic '{topic}'"})

            else:
                return json.dumps({"status": "error", "message": "Unknown command"})
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": "Invalid JSON format"})

    async def create_topic(self, topic):
        if topic in self.topics:
            return json.dumps({"status": "error", "message": "Topic already exists"})
        self.topics[topic] = []  # Empty list for messages
        self.subscribers[topic] = set()  # Track subscribers for this topic
        await self.update_indexing_server("add_topic", topic)
        self.log_event(f"Created topic '{topic}'")
        return json.dumps({"status": "success", "message": f"Topic '{topic}' created"})

    async def delete_topic(self, topic):
        if topic not in self.topics:
            return json.dumps({"status": "error", "message": "Topic does not exist"})
        del self.topics[topic]
        del self.subscribers[topic]
        await self.update_indexing_server("delete_topic", topic)
        self.log_event(f"Deleted topic '{topic}'")
        return json.dumps({"status": "success", "message": f"Topic '{topic}' deleted"})

    async def publish(self, topic, message):
        print("Hello from publish")
        print(f"Topic in publish function are: {self.topics}")

        # Check if the topic exists locally
        if topic in self.topics:
            # Store the message in the local topic
            self.topics[topic].append(message)
            self.log_event(f"Published message on topic '{topic}': {message}")
            print(f"Topic in publish function are: {self.topics}")

            # Forward message to all subscribers
            await self.forward_message_to_subscribers(topic, message)
            return json.dumps({"status": "success", "message": f"Message published on topic '{topic}'"})

        # If the topic doesn't exist locally, query the indexing server
        peer_info = await self.query_indexing_server(topic)
        print(f"Peer Info is: {peer_info}")

        # If peer_info is None, the topic doesn't exist in the indexing server either
        if not peer_info:
            self.log_event(f"Topic '{topic}' not found")
            return json.dumps({"status": "error", "message": f"Topic '{topic}' not found"})

        # If peer_info is valid, forward the publish request to the correct peer
        peer_host, peer_port = peer_info
        if peer_host == self.host and peer_port == self.port:
            # Avoid looping by returning an error when the current peer is both the sender and supposed host
            self.log_event(f"Cannot publish to topic '{topic}' because it does not exist on this peer.")
            return json.dumps({"status": "error", "message": f"Topic '{topic}' does not exist on this peer."})

        # Forward the publish request to the host of the topic
        return await self.forward_publish(peer_host, peer_port, topic, message)

    async def forward_message_to_subscribers(self, topic, message):
        """Forward the message to all subscribers of the given topic."""
        print("Hi from forward message to subscribers")
        subscribers = self.subscribers.get(topic, [])
        print(f"Subscribers are: {subscribers}")
        for subscriber_port in subscribers:
            # Send the message to each subscriber
            try:
                reader, writer = await asyncio.open_connection(self.host, subscriber_port)
                publish_request = json.dumps({"command": "receive_message", "topic": topic, "message": message})
                writer.write(publish_request.encode())
                await writer.drain()
                response = await reader.read(1024)
                self.log_event(f"Sent message to subscriber {subscriber_port}: {response.decode()}")
                print(f"Sent message to subscriber {subscriber_port}: {response.decode()}")
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                print(f"Error sending message to subscriber {subscriber_port}: {e}")
                
    async def handle_subscription(self, topic, subscriber_port):
        """Handle subscription requests from other peers."""
        if topic in self.topics:
            # Add the subscriber port to the subscribers list for the topic
            self.subscribers[topic].add(subscriber_port)
            self.log_event(f"Peer {subscriber_port} subscribed to topic '{topic}'")
            return json.dumps({"status": "success", "message": f"Subscribed to topic '{topic}'"})
        return json.dumps({"status": "error", "message": "Topic not found"})

    async def subscribe(self, topic):
        peer_info = await self.query_indexing_server(topic)  # Find the host of the topic
        if peer_info:
            peer_host, peer_port = peer_info
            # Forward the subscription request to the host peer (5556)
            response = await self.forward_subscribe(peer_host, peer_port, topic)
            if json.loads(response).get("status") == "success":
                self.log_event(f"Subscribed to topic '{topic}' on {peer_host}:{peer_port}")
                return response
        return json.dumps({"status": "error", "message": "Topic not found"})

    async def pull(self, topic):
        if topic in self.topics:
            messages = self.topics[topic]
            if messages:
                # Mark that the subscriber has pulled the messages
                self.subscribers[topic][self.port] = True
                self.log_event(f"Pulled messages from topic '{topic}': {messages}")

                # Check if all subscribers have pulled the messages
                all_pulled = all(self.subscribers[topic].values())
                if all_pulled:
                    # Clear messages only if all subscribers have pulled
                    self.topics[topic] = []  # Clear messages after all subscribers have pulled
                    self.log_event(f"All subscribers pulled messages, clearing messages for topic '{topic}'")

                return json.dumps({"status": "success", "messages": messages})
            else:
                return json.dumps({"status": "error", "message": "No messages to pull"})
        return json.dumps({"status": "error", "message": "Topic not found"})

    async def auto_pull_messages(self, topic):
        """Periodically pull new messages for the topic."""
        while self.port in self.subscribers.get(topic, []):  # Check if still subscribed
            await asyncio.sleep(5)  # Poll every 5 seconds
            response = await self.pull(topic)
            messages = json.loads(response).get('messages', [])
            if messages:
                print(f"[AUTO-PULL] Pulled new messages for topic '{topic}': {messages}")
            # else:
            #     print(f"[AUTO-PULL] No new messages for topic '{topic}'.")

    async def forward_publish(self, peer_host, peer_port, topic, message):
        try:
            reader, writer = await asyncio.open_connection(peer_host, peer_port)
            publish_request = json.dumps({"command": "publish", "topic": topic, "message": message})
            writer.write(publish_request.encode())
            await writer.drain()
            response = await reader.read(1024)
            writer.close()
            await writer.wait_closed()
            return response.decode()
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Failed to publish to topic '{topic}'"})

    async def forward_subscribe(self, peer_host, peer_port, topic):
        """Forward the subscription request to the host peer of the topic."""
        try:
            reader, writer = await asyncio.open_connection(peer_host, peer_port)
            # Send the subscribing peer's port (self.port) to the host
            subscribe_request = json.dumps({
                "command": "subscribe_to_peer", 
                "topic": topic, 
                "subscriber_port": self.port  # Send this peer's port (e.g., 5557) to the host
            })
            writer.write(subscribe_request.encode())
            await writer.drain()
            response = await reader.read(1024)
            writer.close()
            await writer.wait_closed()
            return response.decode()
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Failed to subscribe to topic '{topic}'"})

    async def register_with_indexing_server(self):
        reader, writer = await asyncio.open_connection(self.indexing_server_host, self.indexing_server_port)
        register_request = json.dumps({"command": "register_peer", "host": self.host, "port": self.port})
        writer.write(register_request.encode())
        await writer.drain()
        response = await reader.read(1024)
        self.log_event(f"Registered with indexing server: {response.decode()}")
        writer.close()
        await writer.wait_closed()

    async def update_indexing_server(self, operation, topic):
        reader, writer = await asyncio.open_connection(self.indexing_server_host, self.indexing_server_port)
        update_request = json.dumps({"command": operation, "host": self.host, "port": self.port, "topic": topic})
        writer.write(update_request.encode())
        await writer.drain()
        response = await reader.read(1024)
        self.log_event(f"Indexing server update: {response.decode()}")
        writer.close()
        await writer.wait_closed()

    async def query_indexing_server(self, topic):
        reader, writer = await asyncio.open_connection(self.indexing_server_host, self.indexing_server_port)
        query_request = json.dumps({"command": "query_topic", "topic": topic})
        writer.write(query_request.encode())
        await writer.drain()
        response = await reader.read(1024)
        writer.close()
        await writer.wait_closed()
        response_data = json.loads(response.decode())
        if response_data.get("status") == "success":
            return response_data.get("host"), response_data.get("port")
        return None

    def log_event(self, event):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as log:
            log.write(f"[{timestamp}] {event}\n")
        print(f"[LOG] {event}")


def main():
    parser = argparse.ArgumentParser(description="P2P Publisher-Subscriber Peer Node")
    parser.add_argument('--host', type=str, default='localhost', help='Host address of the peer node')
    parser.add_argument('--port', type=int, default=5555, help='Port to use for the peer node')
    parser.add_argument('--indexing_server_host', type=str, default='localhost', help='Indexing server host address')
    parser.add_argument('--indexing_server_port', type=int, default=6000, help='Indexing server port')
    args = parser.parse_args()

    node = PeerNode(args.host, args.port, args.indexing_server_host, args.indexing_server_port)
    try:
        asyncio.run(node.start())
    except KeyboardInterrupt:
        print("Shutting down peer node.")
        node.running = False


if __name__ == "__main__":
    main()
