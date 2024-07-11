import queue  # for queuing sound data
from matplotlib.animation import FuncAnimation  # for updating plot
import matplotlib.pyplot as plt  # for plot itself
import numpy as np  # for using np arrays
import sounddevice as sd  # for getting sound as input

device = 0  # id of the audio device by default
window = 1000  # window for the data
downsample = 1  # how much samples to drop
channels = [1]  # a list of audio channels
interval = 30  # time interval for plot update
freq_counter = 100  # is limit of x axis

samplerate = sd.query_devices(device, 'input')['default_samplerate']

q = queue.Queue()  # for creating queues to get voice data in order

freq_data = np.zeros((1, freq_counter))
# will be y_axis in plot, contains dominant frequency data

fig, ax = plt.subplots(figsize=(10, 5))  # fig and axis in plot
plt.ylim(0, 600)  # we want freqs between 0-600

line, = ax.plot([], [], 'r-')

is_paused = False  # Global variable to track the pause state

def audio_callback(indata, frames, time, status):
    if is_paused:  # Skip processing if paused
        return
    # translation in terms of audio, completed
    signal = indata[:, 0]
    fft_result = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(fft_result), 1 / samplerate)
    power = np.abs(fft_result)
    dominant_freq = freqs[np.argmax(power)]

    # if freq is between 600-0 is a meaningful freq, so we just want them
    if 600 > dominant_freq > 0:
        q.put([dominant_freq])  # adding to queue

def init():  # init func for animation
    return line,

i = 0  # counts number of dominant_freqs, is significant for updating x-axis

def update_plot(frame):
    global i
    global freq_data

    if is_paused:  # Skip updating if paused
        return line,

    while True:
        try:
            data = q.get_nowait()  # getting dominant_freqs while there are in queue
        except queue.Empty:
            break  # if queue is empty, break and return line
        shift = 1  # shift = 1 since len(data) is always equal to 1

        # i < freq_counter means there is no rolling, data fits in first plot
        if i < freq_counter:
            freq_data[0, i] = data[0]  # adding first <freq_counter> data
            ax.set_xlim(0, freq_counter)
            line.set_data(np.arange(i), freq_data[0, :i])
        # if not, we have to roll to add new data in plot
        else:
            freq_data = np.roll(freq_data, -shift, axis=1)  # rolling freq_data array by 1
            freq_data[0, freq_counter - 1] = data[0]  # changing last data in array
            ax.set_xlim(i - freq_counter, i)
            line.set_data(np.arange(i - freq_counter, i), freq_data[0])
        i += 1
    return line,

def toggle_pause(event):
    global is_paused
    if event.key == 'z':
        is_paused = not is_paused
        if is_paused:
            print("Paused")
        else:
            print("Resumed")

# sound input
stream = sd.InputStream(device=device, channels=max(channels), samplerate=samplerate, callback=audio_callback)

# animation to update plot
animation = FuncAnimation(fig, update_plot, init_func=init, interval=interval, blit=True)

fig.canvas.mpl_connect('key_press_event', toggle_pause)

with stream:
    plt.show()


    '''Örnek Frekans Değerleri
Do (C4) notası: Yaklaşık 261.63 Hz
Re (D4) notası: Yaklaşık 293.66 Hz
Mi (E4) notası: Yaklaşık 329.63 Hz
Fa (F4) notası: Yaklaşık 349.23 Hz
Sol (G4) notası: Yaklaşık 392.00 Hz
La (A4) notası: 440.00 Hz
Si (B4) notası: Yaklaşık 493.88 Hz

y eksenindeki 0-600 aralığı notalar şeklinde ayarlancak 

plotun görünümü iyileştirilecek 


'''