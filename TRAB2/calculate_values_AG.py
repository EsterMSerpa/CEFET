import numpy as np
import random
import pandas as pd

# Valores comerciais (E12 simplificados)
resistores_comerciais = [1, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2, 10]
resistores_comerciais = [r * 10**e for e in range(-1, 3) for r in resistores_comerciais]  # de 0.1 a 1000

# Conversores
def buck(Vin, Vout, Iout, f, L, C, R):
    return abs(Vout - (Vin * (R / (R + L * f))))

def boost(Vin, Vout, Iout, f, L, C, R):
    return abs(Vout - (Vin / (1 - (R / (R + L * f + 1e-9)))))

def buck_boost(Vin, Vout, Iout, f, L, C, R):
    return abs(Vout - (Vin * (R / (R + L * f + 1e-9)) / (1 - R / (R + L * f + 1e-9))))

def cuk(Vin, Vout, Iout, f, L, C, R):
    return abs(Vout - (Vin * (R / (R + L * f + 1e-9)) * (C / (C + R))))

# Algoritmo genético com ajustes realistas
def genetic_algorithm(converter, Vout, Iout, generations=500, population_size=80):
    population = [{
        'Vin': random.uniform(5, 40),
        'f': random.uniform(60, 100),  # Frequência entre 60 e 100 Hz
        'L': random.uniform(100e-6, 1e-3),  # 100µH a 1mH
        'C': random.uniform(100e-9, 1e-6),  # 100nF a 1µF
        'R': random.choice(resistores_comerciais)
    } for _ in range(population_size)]

    for _ in range(generations):
        fitness = [converter(ind['Vin'], Vout, Iout, ind['f'], ind['L'], ind['C'], ind['R']) for ind in population]
        selected = [population[i] for i in np.argsort(fitness)[:population_size // 2]]

        new_population = []
        for _ in range(population_size // 2):
            p1, p2 = random.sample(selected, 2)
            child = {k: (p1[k] + p2[k]) / 2 for k in p1}
            if random.random() < 0.1:
                key = random.choice(list(child.keys()))
                if key == 'R':
                    child['R'] = random.choice(resistores_comerciais)
                else:
                    child[key] *= random.uniform(0.9, 1.1)
            new_population.append(child)
        
        population = selected + new_population

    best = min(population, key=lambda ind: converter(ind['Vin'], Vout, Iout, ind['f'], ind['L'], ind['C'], ind['R']))
    return best

def goal_seek(converter, target_vout, target_iout, params, variable='Vin', tolerance=0.05, max_iter=1000):
    """
    Ajusta uma variável (ex: Vin) para que o Vout se aproxime de target_vout.
    """
    step = 0.1
    direction = 1
    iter_count = 0

    def error(vout_calc):
        return abs(vout_calc - target_vout)

    while iter_count < max_iter:
        vout_calc = converter(params['Vin'], target_vout, target_iout, params['f'], params['L'], params['C'], params['R'])

        if error(vout_calc) <= tolerance:
            break  # Achou um valor aceitável

        # Ajusta variável escolhida
        if variable == 'Vin':
            params['Vin'] += step * direction
        elif variable == 'R':
            params['R'] += step * direction
        elif variable == 'f':
            params['f'] += step * direction
        elif variable == 'L':
            params['L'] += step * 1e-4 * direction
        elif variable == 'C':
            params['C'] += step * 1e-7 * direction
        else:
            raise ValueError("Variável para ajustar inválida")

        # Alterna direção se necessário (p/ evitar travamento)
        if iter_count % 50 == 0 and iter_count != 0:
            direction *= -1

        iter_count += 1

    return params

def main():
    values_df = {'Type': []}
    converters = {
        'buck': buck,
        'boost': boost,
        'buck-boost': buck_boost,
        'cuk': cuk
    }
    Vout = 12 #TESTE
    Iout = 2 #TESTE
    for name, func in converters.items():
        result = genetic_algorithm(func, Vout, Iout)
        result_adjusted = goal_seek(func, Vout, Iout, result.copy(), variable='Vin')  # Ajustando VIN
        values_df['Type'].append(name)
        for key in result_adjusted:
            values_df.setdefault(key, []).append(round(result_adjusted[key], 6))


    df = pd.DataFrame(values_df)
    print(df.to_string(index=False))
    

if __name__ == "__main__":
    main()
    x = 0
