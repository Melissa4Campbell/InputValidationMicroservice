# Input Validation Microservice

## What this microservice does
The Input Validation microservice checks whether the input follows a rule and states whether it is valid. It does not know anything about your program, so it works with any program.

This microservice can do three actions:
*  `check_text`: check that text is between a minimum and maximum length
*  `check_number`: check that a value is a number between a minimum and a maximum
*  `check_choice`: check that a value is one of a list of allowed choices

The microservice uses ZeroMQ with the Request Reply pattern and listens on port 5563. All messages are JSON text.


## How to run it
1. Install the ZeroMQ library for Python: `pip install pyzmq`
2. Start the service and leave it running: `python input_validation_service.py`
3. Stop it with **Control + C**

On Windows, use `py` instead of `python`.

## How to REQUEST data from the microservice
The calling program connects a ZeroMQ REQ socket to `tcp://localhost:5563`, turns its request dictionary into JSON text with `json.dumps`, and sends it.
It sends one request at a time and gets exactly one reply for each request.

Request Parameters:
* `action` (required): `"check_text"`, `"check_number"`, or `"check_choice"`
* `value` (required): the input to check, always sent as a string
* `min_length` and `max_length` (required for `check_text`): minimum and maximum number of characters allowed
* `min` and `max` (required for `check_number`): minimum and maximum limit for a value
* `allowed` (required for `check_choice`): a list of allowed choices to check against a value

Example request call (Python with pyzmq):

```python
import json
import zmq

PORT = 5563

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:" + str(PORT))

request = {
    "action": "check_text",
    "value": "Aria",
    "min_length": 1,
    "max_length": 50
}
socket.send_string(json.dumps(request))
```
The other two actions are sent the same way, with different fields:
```python
{"action": "check_number", "value": "42", "min": 0, "max": 100}
{"action": "check_choice", "value": "elf", "allowed": ["elf", "dwarf", "human"]}
```

## How to RECEIVE data from the microservice
After sending, the program waits for the reply on the same socket with `recv_string`, then turns the JSON text back into a Python dictionary with `json.loads`.

There are three kinds of reply:
* The input is valid: `{"status": "ok", "valid": true}`
* The input breaks a rule: `{"status": "ok", "valid": false, "reason": "..."}`
* The request itself is wrong (missing field or unknown action): `{"status": "error", "message": "..."}`. The service keeps running after this error, so it can answer the next request.

Possible reasons when `valid` is false:
* `Text is shorter than the minimum length of <min_length>`
* `Text is longer than the maximum length of <max_length>`
* `Value is smaller than the minimum of <min>`
* `Value is larger than the maximum of <max>`
* `Value is not a number`
* `Value is not in the allowed list`

Possible error messages:
* `Missing required field: <field name>`
* `Unknown action: <action>`

Example receive call:
```python
reply = json.loads(socket.recv_string())

if reply["status"] == "error":
    print(reply["message"])
elif reply["valid"]:
    print("Input is fine")
else:
    print(reply["reason"])
```

Example reply for the request above:
```json
{"status": "ok", "valid": true}
```

## UML sequence diagram
This diagram shows 

## How to test it
1. Start the microservice and leave it running: `python input_validation_service.py`
2. Open a second terminal window in the same folder and run the test program: `python test_input_validation.py`
3. The test program prints each request, each reply, and **PASS** or **FAIL** for each test. The microservice window shows each request it received and each reply it sent.

The 12 tests cover all three actions, invalid input, a missing field, an unknown action, a valid request right after an error, and a speed check with 100 allowed choices.

On Windows, use `py` instead of `python`.