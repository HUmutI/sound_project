import queue
import sys
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

device = 0 # id of the audio device by default
window = 1000 # window for the data
downsample = 1 # how much samples to drop
channels = [1] # a list of audio channels
duration = 1

samplerate = sd.query_devices(device, 'input')['default_samplerate']

length  = int(window*samplerate/(500*downsample))
# Ses verisini al

fig, ax = plt.subplots(figsize=(10, 5))

line, = ax.plot([], [], lw=2)
ax.set_ylim(0, 600)
xdata, ydata = [], []

def init():
    line.set_data([], [])
    return line,


def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    signal = indata[:, 0]
    fft_result = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(fft_result), 1 / samplerate)
    power = np.abs(fft_result)
    dominant_freq = freqs[np.argmax(power)]
    
    if 0 < dominant_freq < 600:
        xdata.append(len(xdata))
        ydata.append(dominant_freq)
        
        if len(xdata) > 100:
            ax.set_xlim(len(xdata) - 100, len(xdata))
            
        else:
            ax.set_xlim(0, 100)
        
        line.set_data(xdata, ydata)
    
def update_plot(frame):
    return line,

stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=samplerate)
stream.start()

animation = FuncAnimation(fig, update_plot,init_func=init, interval=1000,blit = True)
plt.show()

stream.stop()
stream.close()

'''Örnek Frekans Değerleri
Do (C4) notası: Yaklaşık 261.63 Hz
Re (D4) notası: Yaklaşık 293.66 Hz
Mi (E4) notası: Yaklaşık 329.63 Hz
Fa (F4) notası: Yaklaşık 349.23 Hz
Sol (G4) notası: Yaklaşık 392.00 Hz
La (A4) notası: 440.00 Hz
Si (B4) notası: Yaklaşık 493.88 Hz
'''