import numpy as np
import random
import pandas as pd

# Funções de conversores
def buck(Vin, Vout, Iout, f, L, C, R):
    return Vin * (1 - (Vout / Vin)) - Iout * R

def boost(Vin, Vout, Iout, f, L, C, R):
    return Vin * (1 + (Vout / Vin)) - Iout * R

def buck_boost(Vin, Vout, Iout, f, L, C, R):
    return Vin * (Vout / (Vin - Vout)) - Iout * R

def cuk(Vin, Vout, Iout, f, L, C, R):
    return Vin * (Vout / (Vin + Vout)) - Iout * R

# Função auxiliar para gerar resistores comerciais (E12)
def get_commercial_resistor():
    e12_series = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
    base = random.choice(e12_series)
    multiplier = 10 ** random.randint(0, 2)  # Gera valores entre 1Ω e 820Ω
    return base * multiplier

# Algoritmo genético com restrições
def genetic_algorithm(converter, Vout, Iout, generations=1000, population_size=100):
    population = [{'Vin': random.uniform(0, 100),
                   'f': random.uniform(60, 100),  # Frequência entre 60 e 100 Hz
                   'L': random.uniform(0.1, 10),  # Evita indutância zero
                   'C': random.uniform(0.1, 10),
                   'R': get_commercial_resistor()} for _ in range(population_size)]
    
    for generation in range(generations):
        fitness = [abs(converter(ind['Vin'], Vout, Iout, ind['f'], ind['L'], ind['C'], ind['R'])) for ind in population]
        selected = [population[i] for i in np.argsort(fitness)[:population_size // 2]]
        
        new_population = []
        for _ in range(population_size // 2):
            p1, p2 = random.sample(selected, 2)
            child = {}
            for k in p1:
                if k == 'R':
                    child[k] = get_commercial_resistor()
                else:
                    child[k] = (p1[k] + p2[k]) / 2
            if random.random() < 0.1:
                param = random.choice(list(child.keys()))
                if param != 'R':
                    child[param] *= random.uniform(0.9, 1.1)
            new_population.append(child)
        
        population = selected + new_population
    
    best = population[np.argmin([abs(converter(ind['Vin'], Vout, Iout, ind['f'], ind['L'], ind['C'], ind['R'])) for ind in population])]
    return best

# Parâmetros desejados
Vout = 12
Iout = 2

def main():
    Va = 5
    Ia = 1
    values_df = {}

    types = ['buck', 'boost', 'buck-boost', 'cuk']
    values_df['Type'] = types

    for ret_type in types:
        if ret_type == 'buck':
            comp_values = genetic_algorithm(buck, Vout, Iout)
        elif ret_type == 'boost':
            comp_values = genetic_algorithm(boost, Vout, Iout)
        elif ret_type == 'buck-boost':
            comp_values = genetic_algorithm(buck_boost, Vout, Iout)
        elif ret_type == 'cuk':
            comp_values = genetic_algorithm(cuk, Vout, Iout)

        if 'Vin' not in values_df:
            values_df.update(comp_values)
        else:
            if not isinstance(values_df['Vin'], list):
                for key in ['Vin', 'f', 'L', 'C', 'R']:
                    values_df[key] = [values_df[key]]
            for key in ['Vin', 'f', 'L', 'C', 'R']:
                values_df[key].append(comp_values[key])

    values_df = pd.DataFrame(values_df)
    print(values_df.to_string(index=False))

if __name__ == "__main__":
    main()
