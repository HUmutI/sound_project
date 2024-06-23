import pyaudio
import time
from math import log10
import audioop  
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import multiprocessing
multiprocessing.freeze_support()
def plot(datax, datay):
    x = datax
    y = datay**2
    plt.scatter(x, y)
    plt.legend()
    plt.show()
    
p = pyaudio.PyAudio()
WIDTH = 2
RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
DEVICE = p.get_default_input_device_info()['index']
rms = 1
print(p.get_default_input_device_info())

def callback(in_data, frame_count, time_info, status):
    if __name__ == "__main__":
        global rms
        rms = audioop.rms(in_data, WIDTH) 
        p = multiprocessing.Process(target=plot, args=(rms,0.1))
        p.start()
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
    db = 20 * log10(rms+0.000000001)
    print(f"RMS: {rms} DB: {db}") 
    # refresh every 0.3 seconds 
    time.sleep(0.3)

stream.stop_stream()
stream.close()

p.terminate()