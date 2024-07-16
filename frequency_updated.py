import queue  # for queuing sound data
from matplotlib.animation import FuncAnimation  # for updating plot
import matplotlib.pyplot as plt  # for plot itself
import numpy as np  # for using np arrays
import sounddevice as sd  # for getting sound as input
import time

device = 0  # id of the audio device by default
channels = [1]  # a list of audio channels
interval = 0 # time interval for plot update
x_limit = 10  # is limit of x axis
last_check = time.time()
total_time = 0


samplerate = sd.query_devices(device, 'input')['default_samplerate'] #setting samplerate as default of sound device

q = queue.Queue()  # for creating queues to get voice data in order

time_data = np.zeros([])
freq_data = np.zeros([])# will be y_axis in plot, contains dominant frequency data

fig, ax = plt.subplots(figsize=(15, 6))  # fig and axis in plot

plt.ylim(0, 600)  # we want freqs between 0-600
plt.xlim(0,x_limit) 
plt.xlabel("Hüseyin Umut Işık\nEmir Şahin")
plt.gca().get_yaxis().set_visible(False)




note_ranges = {
        "Do (C4)": (245, 275, "yellow"),
        "Re (D4)": (275, 305,"green"),
        "Mi (E4)": (315, 340,"blue"),
        "Fa (F4)": (340, 365,"red"),
        "Sol (G4)": (375, 410,"purple"),
        "La (A4)": (425, 460,"cyan"),
        "Si (B4)": (475, 505,"orange"),
    }
fig.text(0.124,0.457, "Do (C4)", ha="right", va="top", fontsize=11)
fig.text(0.124,0.497, "Re (D4)", ha="right", va="top", fontsize=11)
fig.text(0.124,0.543, "Mi (E4)", ha="right", va="top", fontsize=11)
fig.text(0.124,0.578, "Fa (F4)", ha="right", va="top", fontsize=11)
fig.text(0.124,0.630, "Sol (G4)", ha="right", va="top", fontsize=11)
fig.text(0.124,0.691, "La (A4)", ha="right", va="top", fontsize=11)
fig.text(0.124,0.754, "Si (B4)", ha="right", va="top", fontsize=11)

'''Örnek Frekans Değerleri
Do (C4) notası: Yaklaşık 261.63 Hz
Re (D4) notası: Yaklaşık 293.66 Hz
Mi (E4) notası: Yaklaşık 329.63 Hz
Fa (F4) notası: Yaklaşık 349.23 Hz
Sol (G4) notası: Yaklaşık 392.00 Hz
La (A4) notası: 440.00 Hz
Si (B4) notası: Yaklaşık 493.88 Hz
'''
x  = np.linspace(-400, 400, 100)
for note in note_ranges:
    low = note_ranges[note][0]
    high = note_ranges[note][1]
    color = note_ranges[note][2]
    y1 = np.linspace(low, low, 100)
    y2 = np.linspace(high, high, 100)
    ax.fill_between(x, y1, y2, where=(y1 < y2), interpolate=True, color=color, alpha=0.3)
    


left_top_text = fig.text(0.10, 1, "press c to clear plot\npress p to pause and continue plot", ha='left', va='top', fontsize=10, color='blue')
right_top_text = fig.text(0.70, 1, "press right arrow button to move plot right\npress left arrow button to move plot left\n\
press z to move to x = 0", ha='left', va="top", fontsize=10, color="blue")
# explanations about keys


line, = ax.plot([], [])
line.set(color='#000000', linewidth=2.5)

is_paused = False  # Global variable to track the pause state

def audio_callback(indata, frames, time_info, status):
    global last_check, total_time, time_data
    
    if is_paused:  # Skip processing if paused
        return
    # translation in terms of audio, completed

    current_time = time.time()

    signal = indata[:, 0]
    fft_result = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(fft_result), 1 / samplerate)
    power = np.abs(fft_result)
    dominant_freq = freqs[np.argmax(power)]
    
    rms = np.sqrt(np.mean(signal**2))
    if rms > 0:
        dB = 20 * np.log10(rms + 0.0000001) + 100
    else:
        dB = -np.inf

    # if freq is between 600-0 is a meaningful freq, so we just want them
    if current_time - last_check >= 0.1:
        if (600 > dominant_freq > 0 and 52 < dB < 100):
            last_check = current_time
            q.put([dominant_freq,total_time]) # adding to queue
            total_time += 0.1 

def init():  # init func for animation
    return line,

i = 0  # counts number of dominant_freqs, is significant for updating x-axis

def update_plot(frame):
    global i
    global freq_data
    global time_data

    if is_paused:# Skip updating if paused
        line.set_data(time_data[ :i], freq_data[ :i])# keep updating line to be able to clear plot when paused
        return line,

    while True:
        try:
            data = q.get_nowait()  # getting dominant_freqs while there are in queue
        except queue.Empty:
            break  # if queue is empty, break and return line
    
        freq_data = np.append(freq_data, data[0])  # adding data
        time_data = np.append(time_data, data[1])
        line.set_data(time_data[ :i], freq_data[ :i]) # setting data into line
        i += 1
    return line,

def toggle_pause(event):
    global is_paused
    global i
    
    if event.key == 'p': # if <key> is pressed, stop or continue
        is_paused = not is_paused
    
def clear_plot(event):
    global i
    global freq_data
    global time_data
    global last_check
    global total_time
    if event.key == 'c': 
        freq_data = np.array([])# clearing array
        time_data = np.array([])
        last_check = time.time()
        total_time = 0
        i = 0 # clearing x axis
        ax.set_xlim(0,x_limit) # for moving the plot 
        fig.canvas.draw() # to x = 0
def move_plot(event):
    global i
    xlim = ax.get_xlim() 
    step = 0.1 * (xlim[1] - xlim[0]) # moving 1/10 of current x_limit at a time
    if (event.key == 'right' or event.key == 'd'):
        ax.set_xlim(xlim[0] + step, xlim[1] + step) # moving plot right
        fig.canvas.draw()
    elif (event.key == 'left' or event.key == 'a'):
        ax.set_xlim(xlim[0] - step, xlim[1] - step) # moving plot left
        fig.canvas.draw()
    elif (event.key == 'z'):
        ax.set_xlim(0,x_limit) # moving plot to x = zero
        fig.canvas.draw()
# sound input
stream = sd.InputStream(device=device, channels=max(channels), samplerate=samplerate, callback=audio_callback)

# animation to update plot
animation = FuncAnimation(fig, update_plot, init_func=init, interval=interval, blit=True)

fig.canvas.mpl_connect('key_press_event', toggle_pause)
fig.canvas.mpl_connect('key_press_event', clear_plot)
fig.canvas.mpl_connect('key_press_event', move_plot)

with stream:
    plt.show()

