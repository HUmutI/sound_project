import pyaudio
import time
from math import log10
import audioop
import keyboard
import matplotlib.pyplot as plt
import matplotlib.animation as animation

detect_list = []
p = pyaudio.PyAudio()
WIDTH = 2
RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
DEVICE = p.get_default_input_device_info()['index']
rms = 1
total_time = 0
interval = 0.3
last_check = time.time()
paused = False
window_start = 0
window_size = 10

# Data for plotting
times = []
decibels = []

def callback(in_data, frame_count, time_info, status):
    global rms
    rms = audioop.rms(in_data, WIDTH)
    return in_data, pyaudio.paContinue

stream = p.open(format=p.get_format_from_width(WIDTH),
                input_device_index=DEVICE,
                channels=1,
                rate=RATE,
                input=True,
                output=False,
                stream_callback=callback)

stream.start_stream()

# Set up the plot
fig, ax = plt.subplots()
line, = ax.plot(times, decibels, 'r-')
ax.set_ylim(0, 100)
ax.set_xlim(window_start, window_start + window_size)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Decibel (dB)')

print("Press 'p' to pause/resume the recording, 'q' to quit.")
print("Use left/right arrow keys to navigate through the graph.")

def update_plot(frame):
    global total_time, last_check, paused, window_start

    if not paused:
        current_time = time.time()
        if current_time - last_check >= interval:
            db = 20 * log10(rms + 0.0000001)
            total_time += interval
            last_check = current_time

            times.append(total_time)
            decibels.append(db)

            if db > 52:
                record_var = f"at the time {round(total_time, 3)} sec and the recorded decibel is {round(db, 3)} dB"
                detect_list.append(record_var)

            if total_time > window_start + window_size:
                window_start = total_time - window_size

            line.set_data(times, decibels)
            ax.set_xlim(window_start, window_start + window_size)
            ax.set_xticks(range(int(window_start), int(window_start + window_size) + 1))
            ax.set_xticklabels([str(int(tick)) for tick in range(int(window_start), int(window_start + window_size) + 1)])

    # Check if "p" key is pressed to pause/resume the script
    if keyboard.is_pressed("p"):
        paused = not paused
        print("Paused" if paused else "Resumed")
        time.sleep(0.2)  # Debounce the key press to avoid multiple toggles

    # Check if "q" key is pressed to stop the script
    if keyboard.is_pressed("q"):
        print("Quitting...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        plt.close(fig)
        return

    # Check if left/right arrow keys are pressed to navigate the graph
    if keyboard.is_pressed("left"):
        window_start = max(0, window_start - 1)
        ax.set_xlim(window_start, window_start + window_size)
        ax.set_xticks(range(int(window_start), int(window_start + window_size) + 1))
        ax.set_xticklabels([str(int(tick)) for tick in range(int(window_start), int(window_start + window_size) + 1)])
        time.sleep(0.1)  # Debounce the key press

    if keyboard.is_pressed("right"):
        window_start = min(total_time - window_size, window_start + 1)
        ax.set_xlim(window_start, window_start + window_size)
        ax.set_xticks(range(int(window_start), int(window_start + window_size) + 1))
        ax.set_xticklabels([str(int(tick)) for tick in range(int(window_start), int(window_start + window_size) + 1)])
        time.sleep(0.1)  # Debounce the key press

    return line,

ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=50)
plt.show()

for var in detect_list:
    print(var)
