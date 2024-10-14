import argparse
import asyncio
from datetime import datetime
import json

class IndexingServer:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.peers = {}  # Tracks active peers and their topics
        self.topics = {}  # Tracks which peer hosts which topic
        self.log_file = "indexing_Server.log"
        self.running = True

    def logging(self, event):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as log:
            log.write(f"[{timestamp}] {event}\n")
        print(f"[LOG] {event}")

    async def start_server(self):
        self.logging(f"Starting the Indexing Server at {self.host}:{self.port}")
        print(f"Starting the Indexing Server at {self.host}:{self.port}")
        server = await asyncio.start_server(self.handle_connection, self.host, self.port)
        async with server:
            self.logging("Indexing Server ready to accept connections")
            print("Indexing Server ready to accept connections")
            await server.serve_forever()

    async def handle_connection(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"[DEBUG] Connection established with {addr}")
        self.logging(f"Connected to {addr}")
        while True:
            try:
                print("Waiting to receive data")
                data = await reader.read(1024)
                if not data:
                    break
                message = data.decode()
                self.logging(f"Received message from {addr}: {message}")
                print(f"Received message from {addr}: {message}")
                response = await self.process_request(message)
                print(f"[DEBUG] Sending response: {response}")
                writer.write(response.encode())
                await writer.drain()
            except Exception as e:
                print(f"Error handling connection: {e}")
                break
        writer.close()
        await writer.wait_closed()

    async def process_request(self, message):
        try:
            request = json.loads(message)
            command = request.get('command')
            if command == "register_peer":
                return await self.register_peer(request)
            elif command == "unregister_peer":
                return await self.unregister_peer(request)
            elif command == "add_topic":
                return await self.add_topic(request)
            elif command == "delete_topic":
                return await self.delete_topic(request)
            elif command == "query_topic":
                return await self.query_topic(request.get('topic'))
            else:
                return json.dumps({"status": "error", "message": "Unknown command"})
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": "Invalid JSON format"})

    async def register_peer(self, request):
        peer_host = request.get('host')
        peer_port = request.get('port')
        self.peers[(peer_host, peer_port)] = []  # Initialize the peer with an empty topic list
        self.logging(f"Registered peer {peer_host}:{peer_port}")
        return json.dumps({"status": "success", "message": f"Peer {peer_host}:{peer_port} registered"})

    async def unregister_peer(self, request):
        peer_host = request.get('host')
        peer_port = request.get('port')
        peer = (peer_host, peer_port)

        if peer in self.peers:
            # Remove the peer and handle its topics
            topics_to_remove = self.peers[peer]
            for topic in topics_to_remove:
                del self.topics[topic]  # Remove topics hosted by this peer
            del self.peers[peer]
            self.logging(f"Unregistered peer {peer_host}:{peer_port} and removed its topics")
            return json.dumps({"status": "success", "message": f"Peer {peer_host}:{peer_port} unregistered and topics removed"})
        else:
            return json.dumps({"status": "error", "message": "Peer not found"})

    async def add_topic(self, request):
        topic = request.get('topic')
        peer_host = request.get('host')
        peer_port = request.get('port')
        if topic not in self.topics:
            self.topics[topic] = (peer_host, peer_port)
            self.peers[(peer_host, peer_port)].append(topic)  # Add topic to peer's list
            self.logging(f"Added topic '{topic}' hosted by {peer_host}:{peer_port}")
            return json.dumps({"status": "success", "message": f"Topic '{topic}' added"})
        else:
            return json.dumps({"status": "error", "message": "Topic already exists"})

    async def delete_topic(self, request):
        topic = request.get('topic')
        if topic in self.topics:
            peer = self.topics[topic]

            # Safely remove the topic from the peer's list
            if topic in self.peers[peer]:
                self.peers[peer].remove(topic)
            else:
                self.logging(f"Topic '{topic}' not found in peer {peer}'s list")

            del self.topics[topic]  # Remove the topic from the host's topic list
            self.logging(f"Deleted topic '{topic}'")

            return json.dumps({"status": "success", "message": f"Topic '{topic}' deleted"})
        else:
            return json.dumps({"status": "error", "message": "Topic not found"})

    async def query_topic(self, topic):
        if topic in self.topics:
            host, port = self.topics[topic]
            print(f"[DEBUG] Topic '{topic}' found at {host}:{port}")
            return json.dumps({"status": "success", "host": host, "port": port})
        else:
            print(f"[ERROR] Topic '{topic}' not found.")
            return json.dumps({"status": "error", "message": "Topic not found"})

def main():
    parser = argparse.ArgumentParser(description="Indexing Server for P2P Publisher-Subscriber System")
    parser.add_argument('--host', type=str, default='localhost', help='Host address of the indexing server')
    parser.add_argument('--port', type=int, default=6000, help='Port to use for the indexing server')
    args = parser.parse_args()

    server = IndexingServer(args.host, args.port)
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("Shutting down indexing server.")
        server.running = False

if __name__ == "__main__":
    main()
    