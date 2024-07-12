import pyaudio
import time
from math import log10
import audioop  
import keyboard

detect_list = []
p = pyaudio.PyAudio()
WIDTH = 2
RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
DEVICE = p.get_default_input_device_info()['index']
rms = 1
total_time = 0
interval = 0.3
last_check = time.time()

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

while stream.is_active():
    current_time = time.time()
    if current_time - last_check >= interval:
        db = 20 * log10(rms + 0.0000001)
        print(f"DB: {db}")
        total_time += interval
        last_check = current_time
        
        if db > 52:
            record_var = f"at the time {round(total_time, 3)} sec and the recorded decibel is {round(db, 3)} dB"
            detect_list.append(record_var)

    # Check if "p" key is pressed to stop the script
    if keyboard.is_pressed("p"):
        break

stream.stop_stream()
stream.close()

for var in detect_list:
    print(var)
p.terminate()
