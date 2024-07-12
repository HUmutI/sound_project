import queue  # for queuing sound data
from matplotlib.animation import FuncAnimation  # for updating plot
import matplotlib.pyplot as plt  # for plot itself
import numpy as np  # for using np arrays
import sounddevice as sd  # for getting sound as input

device = 0  # id of the audio device by default
channels = [1]  # a list of audio channels
interval = 0  # time interval for plot update
x_limit = 250  # is limit of x axis

samplerate = sd.query_devices(device, 'input')['default_samplerate'] #setting samplerate as default of sound device

q = queue.Queue()  # for creating queues to get voice data in order

freq_data = np.zeros([])
# will be y_axis in plot, contains dominant frequency data

fig, ax = plt.subplots(figsize=(15, 5))  # fig and axis in plot

plt.ylim(0, 600)  # we want freqs between 0-600
plt.xlim(0,x_limit) 
plt.ylabel('Frequency (Hz)') # label of axis y

left_top_text = fig.text(0.10, 1, "press c to clear plot\npress p to pause and continue plot", ha='left', va='top', fontsize=10, color='blue')
right_top_text = fig.text(0.70, 1, "press right arrow button to move plot right\n press left arrow button to move plot left\n \
press z to move to x = 0", ha='left', va="top", fontsize=10, color="blue")
# explanations about keys


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

    if is_paused:# Skip updating if paused
        line.set_data(np.arange(i), freq_data[ :i])# keep updating line to be able to clear plot when paused
        return line,

    while True:
        try:
            data = q.get_nowait()  # getting dominant_freqs while there are in queue
        except queue.Empty:
            break  # if queue is empty, break and return line
    
        freq_data = np.append(freq_data, data[0])  # adding data
        line.set_data(np.arange(i), freq_data[ :i]) # setting data into line
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
    if event.key == 'c': 
        freq_data = np.array([])# clearing array
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


    '''Örnek Frekans Değerleri
Do (C4) notası: Yaklaşık 261.63 Hz
Re (D4) notası: Yaklaşık 293.66 Hz
Mi (E4) notası: Yaklaşık 329.63 Hz
Fa (F4) notası: Yaklaşık 349.23 Hz
Sol (G4) notası: Yaklaşık 392.00 Hz
La (A4) notası: 440.00 Hz
Si (B4) notası: Yaklaşık 493.88 Hz
'''