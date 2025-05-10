import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

def get_transfer_function_terms(K, num_factors, den_factors):
    """
    Monta os coeficientes do numerador e denominador a partir dos fatores.

    num_factors: lista de fatores do numerador (ex: [[1, -2, 3]] para s² - 2s + 3)
    den_factors: lista de fatores do denominador (ex: [[1, -0.5], [1, 10], [1, 20]])
    """
    # Numerador
    num = [1]
    for f in num_factors:
        num = np.polymul(num, f)
    num = [K * coef for coef in num]

    # Denominador
    den = [1]
    for f in den_factors:
        den = np.polymul(den, f)

    return num, den

def nyquist_diagram(K,num, den):
    """
    Gera o Diagrama de Nyquist para uma função de transferência definida por num e den.
    """
    sistema = signal.TransferFunction(num, den)
    w = np.logspace(-2, 3, 1000)  # Frequência de 0.01 a 1000 rad/s
    _, H = signal.freqresp(sistema, w)

    plt.figure(figsize=(8, 6))
    plt.plot(H.real, H.imag, label='Nyquist')
    plt.plot(H.real, -H.imag, linestyle='--', color='gray', label='Espelho (simetria)')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.title('Diagrama de Nyquist')
    plt.xlabel('Parte Real')
    plt.ylabel('Parte Imaginária')
    plt.grid(True)
    plt.legend()
    plt.axis('equal')
    plt.savefig(f"C:\\Users\\Desktop\\Documents\\3 - Estudos\\2 - Faculdade\\5 -Repos\\CEFET\\Nyquist\\figures\\diagram with K={K}")


# Uso pro exercício 4: GH(s) = K(s² - 2s + 3) / ((s - 0.5)(s + 10)(s + 20))
K_list = [20,40,120]
num_factors = [[1, -2, 3]]  # s² - 2s + 3
den_factors = [[1, -0.5], [1, 10], [1, 20]] #   (s - 0,5)(s + 10)(s + 20)

for K in K_list:
    num, den = get_transfer_function_terms(K, num_factors, den_factors)
    nyquist_diagram(K,num, den)

x=0