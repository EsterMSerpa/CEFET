import pandas as pd


resistores_comerciais = [1, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2, 10]
resistores_comerciais = [r * 10**e for e in range(-1, 3) for r in resistores_comerciais]  # 0.1 a 1000 ohms

def componentes_conversor(tipo, Vout, Iout, freq, Vin=None, tol=1e-3, max_iter=100):
    """
    tipo: 'buck', 'boost', 'buck-boost', 'cuk'
    Vout: tensão de saída desejada (V)
    Iout: corrente de saída desejada (A)
    freq: frequência de chaveamento (Hz)
    Vin: tensão de entrada (V) [opcional, será estimada se não fornecida]
    tol: tolerância para o ajuste do Vout
    max_iter: número máximo de iterações para o ajuste do L
    """
    T = 1 / freq
    R = Vout / Iout

    def calcula_Vout_estimado(tipo, Vin, L, D):
        # Fórmulas clássicas para estimar Vout dado Vin, L, e D
        if tipo == 'buck':
            return D * Vin
        elif tipo == 'boost':
            return Vin / (1 - D)
        elif tipo == 'buck-boost':
            return -D / (1 - D) * Vin
        elif tipo == 'cuk':
            return -D / (1 - D) * Vin
        else:
            raise ValueError("Tipo inválido.")

    if tipo.lower() == 'buck':
        if Vin is None:
            Vin = Vout / 0.5  # Duty médio de 0.5
        D = Vout / Vin
        IL = Iout
        delta_IL = 0.2 * IL
        L = (Vin - Vout) * D * T / delta_IL
        delta_Vc = 0.01 * Vout
        C = Iout * D * T / (8 * delta_Vc)

        # Ajuste iterativo do L para corrigir Vout
        for _ in range(max_iter):
            Vout_est = calcula_Vout_estimado('buck', Vin, L, D)
            erro = Vout - Vout_est
            if abs(erro) < tol:
                break
            # Ajusta L proporcionalmente (simples)
            # Se Vout_est < Vout, diminuir L para aumentar corrente e melhorar resposta
            L *= (Vout / (Vout_est + 1e-9))

    elif tipo.lower() == 'boost':
        if Vin is None:
            Vin = Vout * 0.5  # Duty médio de 0.5
        D = 1 - Vin / Vout
        IL = Iout / (1 - D)
        delta_IL = 0.2 * IL
        L = Vin * D * T / delta_IL
        delta_Vc = 0.01 * Vout
        C = Iout * T * D / (8 * delta_Vc)

        for _ in range(max_iter):
            Vout_est = calcula_Vout_estimado('boost', Vin, L, D)
            erro = Vout - Vout_est
            if abs(erro) < tol:
                break
            L *= (Vout / (Vout_est + 1e-9))

    elif tipo.lower() == 'buck-boost':
        if Vin is None:
            Vin = Vout / -0.5  # Duty médio de 0.5
        D = Vout / (Vin + Vout)
        IL = Iout / (1 - D)
        delta_IL = 0.2 * IL
        L = Vin * D * T / delta_IL
        delta_Vc = 0.01 * Vout
        C = Iout * T * D / (8 * delta_Vc)

        for _ in range(max_iter):
            Vout_est = calcula_Vout_estimado('buck-boost', Vin, L, D)
            erro = Vout - Vout_est
            if abs(erro) < tol:
                break
            L *= (Vout / (Vout_est + 1e-9))

    elif tipo.lower() == 'cuk':
        if Vin is None:
            Vin = Vout / -0.5
        D = Vout / (Vin + Vout)
        IL = Iout  # Aproximação
        delta_IL = 0.2 * IL
        L1 = Vin * D * T / delta_IL
        L2 = Vout * D * T / delta_IL
        delta_Vc = 0.01 * Vout
        C1 = Iout * T / (8 * delta_Vc)
        C2 = C1
        # Aqui não faço ajuste iterativo, poderia ser implementado similarmente
        return {
            "Vin_estimado": round(Vin, 2),
            "R": round(R, 2),
            "L1": round(L1, 6),
            "L2": round(L2, 6),
            "C1": round(C1, 9),
            "C2": round(C2, 9)
        }

    else:
        raise ValueError("Tipo de conversor inválido. Escolha entre 'buck', 'boost', 'buck-boost' ou 'cuk'.")

    return {
        "Vin_estimado": round(Vin, 2),
        "R": round(R, 2),
        "L": round(L, 6),
        "C": round(C, 9),
        "Vout_estimado": round(Vout_est, 4),
        "erro_Vout": round(erro, 6)
    }


values = []
tipos = ['buck', 'boost', 'buck-boost', 'cuk']
for conversor in tipos:
    values.append(componentes_conversor(conversor, 12, 2, 100, Vin=None))


print(pd.DataFrame(values))
x=0