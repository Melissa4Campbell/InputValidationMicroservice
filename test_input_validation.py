import json
import time
import zmq

PORT = 5563

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:" + str(PORT))


def ask(request):
    print("Sending: " + str(request))
    socket.send_string(json.dumps(request))
    reply = json.loads(socket.recv_string())
    print("Received: " + str(reply))
    return reply

def check(name, passed):
    if passed:
        print("PASS: " + name)
    else:
        print("FAIL: " + name)
    print()


print("Test 1: text within the length limits")
reply = ask({"action": "check_text", "value": "Aria", "min_length": 1, "max_length": 50})
check("check_text accepts 'Aria'", reply["status"] == "ok" and reply["valid"] == True)

print("Test 2: text shorter than the minimum")
reply = ask({"action": "check_text", "value": "", "min_length": 1, "max_length": 50})
check("check_text rejects empty text", "shorter" in reply["reason"] and reply["valid"] == False)

print("Test 3: text longer than the maximum")
reply = ask({"action": "check_text", "value": "A" * 60, "min_length": 1, "max_length": 50})
check("check_text rejects 60 characters and mentions 50", "50" in reply["reason"] and reply["valid"] == False)

print("Test 4: number within range")
reply = ask({"action": "check_number", "value": "42", "min": 0, "max": 100})
check("check_number accepts 42", reply["valid"] == True)

print("Test 5: number above the maximum")
reply = ask({"action": "check_number", "value": "150", "min": 0, "max": 100})
check("check_number rejects 150 and mentions 100", reply["valid"] == False and "100" in reply["reason"])

print("Test 6: value is not a number")
reply = ask({"action": "check_number", "value": "abc", "min": 0, "max": 100})
check("check_number rejects 'abc'", reply["reason"] == "Value is not a number")

print("Test 7: valid request right after an invalid one")
reply = ask({"action": "check_number", "value": "42", "min": 0, "max": 100})
check("a valid request still works after an error", reply["status"] == "ok")

print("Test 8: choice in the allowed list")
reply = ask({"action": "check_choice", "value": "elf", "allowed": ["elf", "dwarf", "human"]})
check("check_choice accepts 'elf'", reply["valid"] == True)

print("Test 9: choice not in the allowed list")
reply = ask({"action": "check_choice", "value": "orc", "allowed": ["elf", "dwarf", "human"]})
check("check_choice rejects 'orc'", reply["reason"] == "Value is not in the allowed list")

print("Test 10: missing required field")
reply = ask({"action": "check_text", "value": "Aria", "min_length": 1})
check("missing max_length gives an error", reply["status"] == "error" and "max_length" in reply["message"])

print("Test 11: unknown action")
reply = ask({"action": "banana", "value": "Aria"})
check("unknown action gives an error", reply["status"] == "error")

print("Test 12: speed with 100 allowed choices")
choices = ["choice " + str(i) for i in range(100)]
started = time.time()
reply = ask({"action": "check_choice", "value": "choice 99", "allowed": choices})
seconds = time.time() - started
print("The reply took " + str(round(seconds, 3)) + " seconds.")
check("100 choices answered in 0.5 seconds or less",
      reply["valid"] == True and seconds <= 0.5)