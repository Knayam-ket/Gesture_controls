import socket
import json
import pydirectinput

UDP_IP = "0.0.0.0"
UDP_PORT = 8080
STEER_THRESHOLD = 3.0  
GAS_THRESHOLD = 3.0    

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

sock.settimeout(0.5)


current_keys = {
    'w': False,
    's': False,
    'a': False,
    'd': False
}

def update_key(key, should_be_pressed):
    """Presses or releases a key only if its state has changed."""
    if should_be_pressed and not current_keys[key]:
        pydirectinput.keyDown(key)
        current_keys[key] = True
        print(f"Holding: {key.upper()}")
    elif not should_be_pressed and current_keys[key]:
        pydirectinput.keyUp(key)
        current_keys[key] = False
        print(f"Released: {key.upper()}")

def release_all_keys():
    """Forces all held keys to release if the phone disconnects."""
    for key in current_keys:
        if current_keys[key]:
            pydirectinput.keyUp(key)
            current_keys[key] = False
            print(f"Stream stopped! Emergency Release: {key.upper()}")

while True:
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8')
        sen_data = json.loads(message)
        
        if "values" in sen_data:
            x, y, z = sen_data["values"]
            
            update_key('a', y < -STEER_THRESHOLD)
            update_key('d', y > STEER_THRESHOLD)
            
            update_key('w', x < -GAS_THRESHOLD)
            update_key('s', x > GAS_THRESHOLD)

    except socket.timeout:
        release_all_keys()
    except json.JSONDecodeError:
        pass
    except Exception as e:
        pass