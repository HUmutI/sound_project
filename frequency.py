import numpy as np
import sounddevice as sd

# Ses verisini alacak parametreler
duration = 5  # kayıt süresi (örneğin 5 saniye)
samplerate = 44100  # örnekleme hızı

# Ses verisini al
print("Ses kaydı başlıyor. Lütfen konuşun...")
recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float64')
sd.wait()

# Fourier dönüşümü uygula
signal = recording.flatten()  # ses verisini düzleştir
fft_result = np.fft.fft(signal)  # Fourier dönüşümü uygula
freqs = np.fft.fftfreq(len(fft_result), 1/samplerate)  # frekans bileşenlerini hesapla

# En yüksek güce sahip frekans bileşenini bul
power = np.abs(fft_result)
dominant_freq = freqs[np.argmax(power)]

print(f"En baskın frekans bileşeni: {dominant_freq} Hz")

'''Örnek Frekans Değerleri
Do (C4) notası: Yaklaşık 261.63 Hz
Re (D4) notası: Yaklaşık 293.66 Hz
Mi (E4) notası: Yaklaşık 329.63 Hz
Fa (F4) notası: Yaklaşık 349.23 Hz
Sol (G4) notası: Yaklaşık 392.00 Hz
La (A4) notası: 440.00 Hz
Si (B4) notası: Yaklaşık 493.88 Hz
'''