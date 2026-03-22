import socket
import json
import pydirectinput

# --- CONFIGURATION ---
UDP_IP = "0.0.0.0"
UDP_PORT = 8080
STEER_THRESHOLD = 3.0  
GAS_THRESHOLD = 3.0    

# Setup Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# --- THE FIX: Add a 0.5 second timeout ---
sock.settimeout(0.5)

print("Racing Controller Started! Waiting for Accelerometer data...")

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

# --- THE FIX: Emergency brake function ---
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
            
            # Steering (Roll / Y-Axis)
            update_key('a', y < -STEER_THRESHOLD)
            update_key('d', y > STEER_THRESHOLD)
            
            # Gas & Brake (Pitch / X-Axis)
            update_key('w', x < -GAS_THRESHOLD)
            update_key('s', x > GAS_THRESHOLD)

    except socket.timeout:
        # If no data arrives for 0.5 seconds, let go of the keyboard!
        release_all_keys()
    except json.JSONDecodeError:
        pass
    except Exception as e:
        pass