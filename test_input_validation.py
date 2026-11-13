import json
import zmq

PORT = 5563

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:" + str(PORT))

requests = [
    {"action": "check_text", "value": "Aria", "min_length": 1, "max_length": 50},
    {"action": "check_text", "value": "", "min_length": 1, "max_length": 50},
    {"action": "check_text", "value": "A" * 60, "min_length": 1, "max_length": 50},
]

for request in requests:
    print("Sending: " + str(request))
    socket.send_string(json.dumps(request))
    reply = json.loads(socket.recv_string())
    print("Received: " + str(reply))