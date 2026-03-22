import socket
import json
import time
import matplotlib.pyplot as plt

UDP_IP = "0.0.0.0"
UDP_PORT = 8080
TIME_WINDOW = 5.0 


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False) 


fig, ax = plt.subplots(figsize=(10, 5))

line_x, = ax.plot([], [], label='X (Pitch)', color='red', linewidth=1)
line_y, = ax.plot([], [], label='Y (Roll)', color='green', linewidth=1)
line_z, = ax.plot([], [], label='Z (Yaw)', color='blue', linewidth=1)

ax.set_title("Real-Time Gyroscope Data")
ax.set_xlabel("Time (Seconds ago)")
ax.set_ylabel("Rotation Velocity")
ax.legend(loc="upper left")

data_buffer = []

print(f"Listening on port {UDP_PORT}... Close the graph window to stop.")

while plt.fignum_exists(fig.number):
    current_time = time.time()

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8')
            sen_data = json.loads(message)

            if "values" in sen_data:
                x, y, z = sen_data["values"]
                data_buffer.append((current_time, x, y, z))
                
    except BlockingIOError:
        pass
    except json.JSONDecodeError:
        pass 
    data_buffer = [item for item in data_buffer if current_time - item[0] < TIME_WINDOW]

    if data_buffer:
        times = [item[0] for item in data_buffer]
        xs = [item[1] for item in data_buffer]
        ys = [item[2] for item in data_buffer]
        zs = [item[3] for item in data_buffer]

      
        relative_times = [t - current_time for t in times]

        line_x.set_data(relative_times, xs)
        line_y.set_data(relative_times, ys)
        line_z.set_data(relative_times, zs)

        ax.set_xlim(-TIME_WINDOW, 0)
        ax.set_ylim(-60, 60)
        all_vals = xs + ys + zs
        
    plt.pause(0.01)

sock.close()
print("Graph closed. Program ended.")