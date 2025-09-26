from matplotlib import pyplot as plt
import numpy as np

def modulacion_pcm(valor, M, polo_uno = 1, duracion_bit = 1):
    num_bits = int(np.log2(M))
    min_valor = np.min(valor)
    max_valor = np.max(valor)
    niveles = np.linspace(min_valor, max_valor, M)
    valores_pcm = np.array([np.argmin(np.abs(niveles - valor_i)) for valor_i in valor])
    arreglo_bin = [format(num, f"0{num_bits}b") for num in valores_pcm]
    bit_stream = [int(bit) for binario in arreglo_bin for bit in binario]
    senial_polar = np.array([polo_uno if bit == 1 else -polo_uno for bit in bit_stream])
    num_bits = len(senial_polar)
    tiempo = np.linspace(0, num_bits * duracion_bit, num_bits, endpoint = False)
    return tiempo, senial_polar, bit_stream
