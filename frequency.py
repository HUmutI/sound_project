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
duration = 5

samplerate = sd.query_devices(device, 'input')['default_samplerate']

length  = int(window*samplerate/(500*downsample))
# Ses verisini al

freq_data = []
data = 0
def update_plot(frame):
    
    try:    
        data = recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float64')
        sd.wait()
    except(sd.PortAudioError):
        data = np.zeros((length,len(channels)))
    signal = data.flatten()  # ses verisini düzleştir
    fft_result = np.fft.fft(signal)  # Fourier dönüşümü uygula
    freqs = np.fft.fftfreq(len(fft_result), 1/samplerate)  # frekans bileşenlerini hesapla
    
    power = np.abs(fft_result)
    dominant_freq = freqs[np.argmax(power)]
    print(f"En baskın frekans bileşeni: {dominant_freq} Hz")
    freq_data.append(dominant_freq)
    
    ax.clear()
    ax.plot(freq_data)
    print(freq_data)

fig,ax = plt.subplots(figsize=(10,10))



animation = FuncAnimation(fig, update_plot, interval=duration*1000)

plt.show()



'''Örnek Frekans Değerleri
Do (C4) notası: Yaklaşık 261.63 Hz
Re (D4) notası: Yaklaşık 293.66 Hz
Mi (E4) notası: Yaklaşık 329.63 Hz
Fa (F4) notası: Yaklaşık 349.23 Hz
Sol (G4) notası: Yaklaşık 392.00 Hz
La (A4) notası: 440.00 Hz
Si (B4) notası: Yaklaşık 493.88 Hz
'''