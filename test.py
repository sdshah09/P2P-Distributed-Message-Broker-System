import socket
import json

def send_command(command, peer_host='localhost', peer_port=5555):
    # Create a socket connection to the peer node
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((peer_host, peer_port))
        # Send the command (convert dictionary to JSON string)
        client_socket.sendall(json.dumps(command).encode('utf-8'))
        # Receive and print the response
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Response: {response}")

# Example usage:

# Create topic
create_topic_cmd = {
    "command": "create_topic",
    "topic": "Sports"
}
send_command(create_topic_cmd)

# Publish message to topic
publish_cmd = {
    "command": "publish",
    "topic": "Sports",
    "message": "Football match tonight!"
}
send_command(publish_cmd)

# Subscribe to topic
subscribe_cmd = {
    "command": "subscribe",
    "topic": "Sports"
}
send_command(subscribe_cmd)

# Pull messages from topic
pull_cmd = {
    "command": "pull",
    "topic": "Sports"
}
send_command(pull_cmd)
