"""// 1. Duas sequencias pra uma maq de estado
// 2. Durante um tempo x a sequência passa de um item pro outro
// 3. Pra começar a sequencia se aperta um botão: se aperta o B1 a seq inicial será s1, se aperta B2 a sequencia inicial é s2
// 4. Um potenciometro determina o tempo de "troca" pra passar de um numero pro outro (se atualiza pegar a "entrada" em cada 0.10seg)  
// 5. De t em t (determinado pelo potenciometro) se le qual botão está pressionado;
    // 5.1 Se o bot pressionado for diferente do último bot pressionado (ou seja se estiver em s1 e eu pressionar b2 pra ir pra s2) se troca a sequencia    
    // 5.2 Ao trocar a sequencia ele encontrar o número maior ou igual mais próximo do último digito e ir pro valor do prox indice  """

import time

 
def loop1 (atual_dig, atual_seq,bot1,bot2):
 
    if (bot1 == True and atual_seq == s2) or (bot2 == True and atual_seq == s1):
        for n,idx in atual_seq:
            if n >= atual_dig: 
                atual_seq = s1 if atual_seq == s2 else s2
                atual_dig=atual_seq[idx]
                break
   
    return atual_dig, atual_seq
 
 
###TEST
 
s1=[10,11,17,12,20,19,18,]
s2=[17,12,18,14,11,1,16,15]
atual_seq = s1
atual_dig = s1[0]
porc_pot = 0.2 #20%
min_v = 100
max_v = 500

while True:
    start_time_loop1 = time.time()
    t_troca = porc_pot*(max_v-min_v)+min_v
    while True:
        if (time.time() - start_time_loop1) < t_troca:
            atual_dig, atual_seq = loop1(atual_dig,atual_seq,True,False)
            print(str(atual_dig)[0])
            print(str(atual_dig)[1])
            
   
    time.sleep(0.10)#em segundos
 