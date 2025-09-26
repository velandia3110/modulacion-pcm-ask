import numpy as np
from matplotlib import pyplot as plt

def modulacion_ask(
    senial_banda_base,
    tiempo,
    frecuencia_portadora=100,
    amplitud_portadora=1.0,
):
    portadora = np.cos(2 * np.pi * frecuencia_portadora * tiempo)
    
    senial_modulada = np.where(senial_banda_base > 0.5, amplitud_portadora * portadora, 0.0)
    return senial_modulada

def modulacion_ask_analoga(senial_analoga, tiempo, frecuencia_portadora=100, amplitud_portadora=1.0, umbral=0.0):
    portadora = np.cos(2 * np.pi * frecuencia_portadora * tiempo)
    senial_modulada = np.where(senial_analoga > umbral, amplitud_portadora * portadora, 0.0)
    return senial_modulada