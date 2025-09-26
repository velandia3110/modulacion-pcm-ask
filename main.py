import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from pcm import modulacion_pcm
from ask import modulacion_ask

if __name__ == "__main__":
    fs, audio = wavfile.read("audio.wav")  
    audio = audio.astype(float)
    
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    audio = audio / np.max(np.abs(audio))

    audio = audio[:2000]

    tiempo_pcm, senial_pcm, bitstream = modulacion_pcm(audio, M=8, polo_uno=1, duracion_bit=1/fs)

    senial_ask = modulacion_ask(senial_pcm, tiempo_pcm, frecuencia_portadora=200, amplitud_portadora=1.0)

    plt.figure(figsize=(12, 10))

    # Señal analógica
    plt.subplot(3, 1, 1)
    plt.plot(audio, label="Señal analógica (Audio)")
    plt.title("Señal Original (Audio)")
    plt.legend()
    plt.grid(True)

    # Señal PCM
    plt.subplot(3, 1, 2)
    plt.step(tiempo_pcm, senial_pcm, where="mid", label="Señal PCM (Polar)")
    plt.title("Señal PCM")
    plt.legend()
    plt.grid(True)

    # Señal ASK
    plt.subplot(3, 1, 3)
    plt.plot(tiempo_pcm, senial_ask, label="Señal ASK")
    plt.title("Señal ASK modulada desde PCM")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
