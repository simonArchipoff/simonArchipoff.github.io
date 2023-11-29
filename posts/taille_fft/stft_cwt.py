import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import chirp, stft, cwt, morlet2,morlet,get_window
from scipy.io.wavfile import write
import time
import scipy.constants as const

# Générer un signal sinusoïdal
fs = 8000  # fréquence d'échantillonnage en Hz
t = np.linspace(0, 1, fs, endpoint=False)  # échantillonnage sur 1 seconde
freq = 300  # fréquence du signal en Hz
#signal_temporel = np.sin(2 * np.pi * freq * t)



def add_with_shift(array1, array2, shift):
    shift=int(shift*len(array1))
    a2 = np.copy(array2)
    if (len(a2) + shift) > len(array1):
        a2 = a2[:len(array1) - shift]
    array1[shift:shift+len(a2)] += a2[:]
    return array1


t = np.linspace(0, 1, fs, endpoint=False)  # échantillonnage sur 1 seconde

signal_temporel = np.random.normal(loc=0, scale=0.0001, size=len(t))

# Ajouter une dirac au milieu

p = int(len(t)*0.9)
signal_temporel[p:p+1] = 1

# Ajouter une ondelette de basse fréquence à partir de l'indice 256
chirp = 0.6*chirp(t,100,1,4000)
chirp = chirp * get_window("hann",len(chirp))

hf = np.sin(t[0:len(t)//50] * 2 * np.pi * 3500)
hf = hf #* get_window("hann",len(hf))


signal_temporel = add_with_shift(signal_temporel,chirp,0)

signal_temporel = add_with_shift(signal_temporel,0.5*hf,0.5)
# Ajouter une ondelette de haute fréquence à partir de l'indice 678
#high_freq_morlet = np.real(morlet(500, 100, complete=True))
#signal_temporel[678:] += high_freq_morlet[:len(t) - 678]



# Afficher le signal temporel
plt.figure(figsize=(10, 6))
plt.subplot(3, 1, 1)
plt.plot(t, signal_temporel)
plt.title('Signal Temporel (composition d\'un chirp, d\'une dirac, et d\'une breve sinusoide)')
plt.xlabel('Temps (s)')
plt.ylabel('Amplitude')
plt.xlim(t[0], t[-1])

# Calculer et afficher la STFT
debut_stft=time.time()
f, t_spec, Zxx = stft(signal_temporel[:-1], fs, nperseg=fs//8,noverlap=(fs//8)-1)
fin_stft = time.time()
#Zxx = Zxx[:,0:-1]
#t_spec = t_spec[0:-1]
plt.subplot(3, 1, 2)
plt.pcolormesh(t_spec, f, np.abs(Zxx), shading='auto')
plt.title(f'Short-Time Fourier Transform (STFT) (temps de calcul : {(fin_stft - debut_stft) * 1000:.2f}ms pour une taille de {len(t_spec)} échantillons par {len(f)} fréquences)')
plt.xlabel(f'Temps (s)')
plt.ylabel(f'Fréquence (Hz)')
#plt.colorbar()

# Calculer et afficher la CWT
freq = np.linspace(10, fs/2, len(f))
w=15.0
widths = w*fs / (2*freq*np.pi)

debut_cwt = time.time()
coefficients = cwt(signal_temporel, morlet2, widths,w=w)
fin_cwt=time.time()
plt.subplot(3, 1, 3)
plt.pcolormesh(t, freq, (np.abs(coefficients)), shading='auto')
plt.title(f'Continuous Wavelet Transform (CWT) (temps de calcul : {(fin_cwt - debut_cwt) * 1000:.2f}ms pour une taille de {len(t)} échantillons par {len(freq)} fréquences)')
plt.xlabel(f'Temps (s)')
plt.ylabel(f'Fréquence (Hz)')
#plt.colorbar()
plt.subplots_adjust(hspace=0.4, wspace=0.5)
#plt.tight_layout()
plt.show()

def write_wav(filename, signal, sample_rate):
    # Assurez-vous que le signal est en valeurs entre -1 et 1
    signal = np.int16(signal / np.max(np.abs(signal)) * 32767)
    # Écrire le fichier WAV
    write(filename, sample_rate, signal)

# Exemple d'utilisation
sample_rate = 44100  # par exemple, fréquence d'échantillonnage de 44,1 kHz
duration = 5  # durée du signal en secondes
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  # vecteur temps
signal = np.sin(2 * np.pi * 440 * t)  # signal sinusoidal de 440 Hz

write_wav('output.wav', signal_temporel, fs)
