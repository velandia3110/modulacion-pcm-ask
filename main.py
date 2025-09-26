import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.io import wavfile
from pcm import modulacion_pcm
from ask import modulacion_ask

def crear_visualizador_sincronizado():
    fs, audio = wavfile.read("audio.wav")  
    audio = audio.astype(float)
    
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    audio = audio / np.max(np.abs(audio))
    
    print(f"Procesando audio completo: {len(audio)/fs:.2f} segundos ({len(audio)} muestras)")
    
    tiempo_audio_completo = np.arange(len(audio)) / fs
    duracion_total_audio = tiempo_audio_completo[-1]
    
    bits_por_muestra = 3  # Para M=8 (log2(8) = 3 bits)
    total_bits_estimado = len(audio) * bits_por_muestra
    
    duracion_bit_sincronizada = duracion_total_audio / total_bits_estimado
    
    print(f"Duración de bit calculada: {duracion_bit_sincronizada*1000:.4f} ms")
    print(f"Bits estimados: {total_bits_estimado}")
    
    max_muestras_por_vez = 5000 
    
    if len(audio) > max_muestras_por_vez:
        factor_reduccion = len(audio) // max_muestras_por_vez
        audio_procesado = audio[::factor_reduccion]
        print(f"Audio reducido por factor {factor_reduccion}: {len(audio_procesado)} muestras")
        
        duracion_bit_final = duracion_total_audio / (len(audio_procesado) * bits_por_muestra)
    else:
        audio_procesado = audio
        duracion_bit_final = duracion_bit_sincronizada
    
    print(f"Duración de bit final: {duracion_bit_final*1000:.4f} ms")
    
    # Modulación PCM
    tiempo_pcm, senial_pcm, bitstream = modulacion_pcm(
        audio_procesado, 
        M=8, 
        polo_uno=1, 
        duracion_bit=duracion_bit_final
    )

    # Modulación ASK
    senial_ask = modulacion_ask(
        senial_pcm, 
        tiempo_pcm, 
        frecuencia_portadora=1000,
        amplitud_portadora=1.0
    )
    
    # VERIFICAR SINCRONIZACIÓN
    duracion_pcm = tiempo_pcm[-1] if len(tiempo_pcm) > 0 else 0
    duracion_ask = tiempo_pcm[-1] if len(tiempo_pcm) > 0 else 0
    
    print(f"\nVERIFICACIÓN DE SINCRONIZACIÓN")
    print(f"Duración audio original: {duracion_total_audio:.3f} s")
    print(f"Duración señal PCM: {duracion_pcm:.3f} s")
    print(f"Duración señal ASK: {duracion_ask:.3f} s")
    print(f"Diferencia PCM vs Audio: {abs(duracion_pcm - duracion_total_audio):.3f} s")
    
    # Configurar ventana de visualización
    ventana_segundos = 0.1  
    duracion_maxima = max(duracion_total_audio, duracion_pcm)
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 13))
    plt.subplots_adjust(bottom=0.1, top=0.94, hspace=0.8)
    
    def actualizar_graficas(tiempo_inicio):
        tiempo_fin = min(tiempo_inicio + ventana_segundos, duracion_maxima)
        
        ax1.clear()
        ax2.clear() 
        ax3.clear()
        
        # Señal de audio original
        mask_audio = (tiempo_audio_completo >= tiempo_inicio) & (tiempo_audio_completo <= tiempo_fin)
        if np.any(mask_audio):
            ax1.plot(tiempo_audio_completo[mask_audio] * 1000, audio[mask_audio], 
                    'b-', linewidth=1.0, label='Audio Original')
        
        ax1.set_title(f'Señal Original ({tiempo_inicio*1000:.0f}-{tiempo_fin*1000:.0f} ms)', pad=20)
        ax1.set_xlabel('Tiempo (ms)', labelpad=10)
        ax1.set_ylabel('Amplitud', labelpad=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(tiempo_inicio * 1000, tiempo_fin * 1000)
        ax1.legend(loc='upper right', fontsize=9)
        
        # Señal PCM
        mask_pcm = (tiempo_pcm >= tiempo_inicio) & (tiempo_pcm <= tiempo_fin)
        if np.any(mask_pcm):
            ax2.step(tiempo_pcm[mask_pcm] * 1000, senial_pcm[mask_pcm], 
                    where="mid", linewidth=1.2, color='green', label='PCM')
        else:
            ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Sin datos PCM')
        
        ax2.set_title('Señal PCM', pad=20)
        ax2.set_xlabel('Tiempo (ms)', labelpad=10)
        ax2.set_ylabel('Amplitud', labelpad=10)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(tiempo_inicio * 1000, tiempo_fin * 1000)
        ax2.set_ylim(-1.5, 1.5)
        ax2.legend(loc='upper right', fontsize=9)
        
        # Señal ASK
        if np.any(mask_pcm):
            ax3.plot(tiempo_pcm[mask_pcm] * 1000, senial_ask[mask_pcm], 
                    'r-', linewidth=0.8, alpha=0.8, label='ASK')
        else:
            ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Sin datos ASK')
        
        ax3.set_title('Señal ASK', pad=20)
        ax3.set_xlabel('Tiempo (ms)', labelpad=10)
        ax3.set_ylabel('Amplitud', labelpad=10)
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim(tiempo_inicio * 1000, tiempo_fin * 1000)
        ax3.legend(loc='upper right', fontsize=9)
        
        plt.draw()
    
    ax_slider = plt.axes([0.15, 0.02, 0.7, 0.025])
    slider = Slider(
        ax_slider, 
        'Tiempo (s)', 
        0, 
        max(0, duracion_maxima - ventana_segundos),
        valinit=0,
        valfmt='%.2f'
    )
    
    slider.on_changed(actualizar_graficas)
    
    # Mostrar gráficas iniciales
    actualizar_graficas(0)
    
    ratio_cobertura = (duracion_pcm / duracion_total_audio) * 100 if duracion_total_audio > 0 else 0
    duracion_str = f"{duracion_total_audio:.1f}s"
    pcm_str = f"{duracion_pcm:.1f}s" 
    cobertura_str = f"{ratio_cobertura:.0f}%"
    
    fig.suptitle(f'Audio: {duracion_str} | PCM: {pcm_str} | Cobertura: {cobertura_str}', 
                 fontsize=11, y=0.97)
    
    print(f"\nCobertura de modulación: {ratio_cobertura:.1f}% del audio original")
    if ratio_cobertura < 95:
        print("Las modulaciones no cubren todo el audio. Esto es normal para audios muy largos.")
    else:
        print("Las modulaciones cubren casi todo el audio.")
    
    plt.show()

if __name__ == "__main__":
    crear_visualizador_sincronizado()