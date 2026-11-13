import json

import zmq

PORT = 5563


def error_reply(message):
    return {"status": "error", "message": message}


def check_text(request):
    value = request["value"]
    min_length = request["min_length"]
    max_length = request["max_length"]

    if len(value) < min_length:
        return {"status": "ok", "valid": False,
                "reason": "Text is shorter than the minimum length of " + str(min_length)}
    if len(value) > max_length:
        return {"status": "ok", "valid": False,
                "reason": "Text is longer than the maximum length of " + str(max_length)}
    return {"status": "ok", "valid": True}


def check_number(request):
    try:
        number = float(request["value"])
    except ValueError:
        return {"status": "ok", "valid": False, "reason": "Value is not a number"}

    minimum = request["min"]
    maximum = request["max"]

    if number < minimum:
        return {"status": "ok", "valid": False,
                "reason": "Value is smaller than the minimum of " + str(minimum)}
    if number > maximum:
        return {"status": "ok", "valid": False,
                "reason": "Value is larger than the maximum of " + str(maximum)}
    return {"status": "ok", "valid": True}


def check_choice(request):
    value = request["value"]
    allowed = request['allowed']

    if value not in allowed:
        return {"status": "ok", "valid": False, "reason": "Value is not in the allowed list"}
    return {"status": "ok", "valid": True}


def handle_request(request):
    action = request.get("action")
    if action == "check_text":
        return check_text(request)
    elif action == "check_number":
        return check_number(request)
    elif action == "check_choice":
        return check_choice(request)
    return error_reply("Unknown action: " + str(action))


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:" + str(PORT))
    print("Input Validation microservice is running on port " + str(PORT))
    print("Press the Control key and the C key together to stop it.")

    try:
        while True:
            if socket.poll(500) == 0:
                continue
            message = socket.recv_string()
            try:
                request = json.loads(message)
                print("Received a request: " + str(request))
                reply = handle_request(request)
            except json.JSONDecodeError:
                print("Received a request that is not valid JSON text")
                reply = error_reply("Request must be valid JSON text")
            except Exception as problem:
                reply = error_reply("Something went wrong: " + str(problem))
            socket.send_string(json.dumps(reply))
            print("Sent a reply: " + str(reply))
    except KeyboardInterrupt:
        print("Input Validation microservice stopped.")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()