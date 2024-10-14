
# P2P Publisher-Subscriber System

This project implements a simple Peer-to-Peer (P2P) publisher-subscriber system using asynchronous Python. Each peer can host topics, subscribe to topics from other peers, and publish messages that are forwarded to all subscribers. A central indexing server helps peers discover which peer is hosting a given topic.

## Table of Contents
- [Overview](#overview)
- [Files](#files)
- [Features](#features)
- [Architecture](#architecture)
- [Components](#components)
  - [Peer Node](#peer-node)
  - [Indexing Server](#indexing-server)
- [How to Run](#how-to-run)
- [Commands](#commands)
- [Examples](#examples)
  - [Creating a Topic](#creating-a-topic)
  - [Subscribing to a Topic](#subscribing-to-a-topic)
  - [Publishing a Message](#publishing-a-message)
- [Test Scenarios](#test-scenarios)
- [Error Handling](#error-handling)

## Overview

- This project demonstrates a simple P2P system where peers can create topics, subscribe to topics hosted by other peers, and publish messages that are forwarded to all subscribers. Peers communicate with each other and the central indexing server using asynchronous I/O.

## Files
### There are 2 main files.
1. IndexingServer which is a centralized indexing server as per the assignment's requirement
2. PeerNode this file contains code for host who can work as publisher or subscriber and will query indexing server according to user's pub sub requirements.

### There are 2 folders.
1. Log Folder:
- This folder contains logs generated during the execution of the system.
- It includes logs for both the Indexing Server and Peer Nodes, which provide detailed records of the actions performed, such as topic creation, subscriptions, and message publishing.
- The logs are automatically created when you run the code, and they are stored in the main folder.
- Note: This folder is provided for your reference to check system actions and ensure correctness.
2. Test Folder:
- This folder contains all the test scripts used for benchmarking and validating the APIs of the P2P Publisher-Subscriber model.
- The test scripts in this folder are used to:
- Benchmark API Performance: Measure the latency and throughput for APIs such as create_topic, subscribe, and publish_message.
- Check API Functionality: Verify that all APIs (e.g., create_topic, subscribe, publish_message, delete_topic) are working correctly.
- Additionally, this folder includes the graph file showing the benchmarking results for the API performance.

## Features

- **Topic Creation**: Peers can create topics and host them.
- **Subscription**: Peers can subscribe to topics hosted by other peers.
- **Message Publishing**: Peers can publish messages to a topic, and the message is forwarded to all subscribers.
- **Central Indexing Server**: Helps peers find which peer is hosting a specific topic.
- **Error Handling**: Handles scenarios such as trying to publish to a non-existing topic or removing topics.

## Architecture

1. **Peer Nodes**: Each peer can create, subscribe to, or publish messages on topics. Peer nodes communicate with each other via TCP.
2. **Indexing Server**: The central server maintains a list of all peer nodes and the topics they host. Peers query this server to find which node is hosting a particular topic.

## Components

### Peer Node

Each peer node is responsible for:
- Creating topics
- Subscribing to topics hosted by other peers
- Publishing messages to a topic
- Forwarding messages to all subscribers

### Indexing Server

The central indexing server keeps track of:
- Active peer nodes
- The topics each peer is hosting
- Providing query functionality for peers to find which peer is hosting a topic

## How to Run

### Prerequisites
- Python 3.8+
- Install dependencies (if any) using `pip install`:
   ```bash
   pip install -r requirements.txt

## Running the Indexing Server

Start the central indexing server before running any peers. The indexing server listens for peers registering or querying for topics.

```python
python IndexingServer.py --host localhost --port 6000
```
## Running Peer Nodes
- In separate terminals, run the peer nodes. Each peer needs to register itself with the indexing server.

```python 
python PeerNode.py --host localhost --port 5555 --indexing_server_host localhost --indexing_server_port 6000
```
```python 
python PeerNode.py --host localhost --port 5556 --indexing_server_host localhost --indexing_server_port 6000
```

```python 
python PeerNode.py --host localhost --port 5557 --indexing_server_host localhost --indexing_server_port 6000
```

## Commands
The following commands are used to interact with the system:

### Create a Topic:

```json
{"command": "create_topic", "topic": "<TOPIC_NAME>"}
```
Subscribe to a Topic:
```json
{"command": "subscribe", "topic": "<TOPIC_NAME>"}
```
Publish a Message:
```json
{"command": "publish", "topic": "<TOPIC_NAME>", "message": "<MESSAGE_CONTENT>"}
```
Pull Messages:
```json
{"command": "pull", "topic": "<TOPIC_NAME>"}
```
Delete a Topic:
```json
{"command": "delete_topic", "topic": "<TOPIC_NAME>"}
```

## Examples
### Creating a Topic
To create a topic on Peer 1 (port 5555), send the following command:

```bash
echo '{"command": "create_topic", "topic": "Sports"}' | ncat localhost 5555
This will create the topic "Sports" on Peer 1.
```
```bash
Subscribing to a Topic
To subscribe Peer 2 (port 5556) and Peer 3 (port 5557) to the "Sports" topic hosted by Peer 1:
```

```bash

echo '{"command": "subscribe", "topic": "Sports"}' | ncat localhost 5556
```
```bash
echo '{"command": "subscribe", "topic": "Sports"}' | ncat localhost 5557
```
- Publishing a Message
To publish a message to the "Sports" topic from Peer 1 (port 5555):

```bash
echo '{"command": "publish", "topic": "Sports", "message": "Football match tonight!"}' | ncat localhost 5555
```
- This will send the message to all peers subscribed to the "Sports" topic (in this case, Peer 2 and Peer 3).

## Test Scenarios
- Creating a Topic: Create a topic on Peer 1 and ensure that other peers can query it via the indexing server.

- Subscribing to a Topic: Have Peer 2 and Peer 3 subscribe to the "Sports" topic hosted on Peer 1.

- Publishing a Message: Publish a message to the "Sports" topic on Peer 1 and verify that Peer 2 and Peer 3 receive it.

- Deleting a Topic: Delete the "Sports" topic on Peer 1 and ensure that no more messages can be published to it.

## Error Handling
### Common Errors:
- Topic Not Found: If a topic doesn't exist when a peer tries to publish a message, the system will return an error message.
- Publishing to a Deleted Topic: If you try to publish to a deleted topic, it will log and return an error.
Example:
```json
{
  "status": "error",
  "message": "Topic 'Sports' not found"
}
```

## Conclusion
This project demonstrates how to build a simple P2P publisher-subscriber system using Python's asynchronous capabilities. It handles topic creation, subscription, and message forwarding across multiple peer nodes, with the help of a central indexing server.

