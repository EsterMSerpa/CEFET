// 1. Duas sequencias pra uma maq de estado
// 2. Durante um tempo x a sequência passa de um item pro outro
// 3. Pra começar a sequencia se aperta um botão: se aperta o B1 a seq inicial será s1, se aperta B2 a sequencia inicial é s2
// 4. Um potenciometro determina o tempo de "troca" pra passar de um numero pro outro (se atualiza pegar a "entrada" em cada 0.10seg)  
// 5. De t em t (determinado pelo potenciometro) se le qual botão está pressionado;
    // 5.1 Se o bot pressionado for diferente do último bot pressionado (ou seja se estiver em s1 e eu pressionar b2 pra ir pra s2) se troca a sequencia    
    // 5.2 Ao trocar a sequencia ele encontrar o número maior ou igual mais próximo do último digito e ir pro valor do prox indice  



#include <avr/io.h>
#define F_CPU 4000000
#include <util/delay.h>
#include <avr/interrupt.h>
#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>

/////////////////////////////////  HARDWARE /////////////////////////////////

#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>

// Sequências fixas
int s1[] = {10, 11, 17, 12, 20, 19, 18};
int s2[] = {17, 12, 18, 14, 11, 1, 16, 15};
int len_s1 = sizeof(s1) / sizeof(s1[0]);
int len_s2 = sizeof(s2) / sizeof(s2[0]);

// Ponteiro para sequência atual
int* atual_seq;
int len_atual_seq;

int atual_dig;

// Função que simula a lógica do loop1
void loop1(bool bot1, bool bot2) {
    int* outra_seq;
    int len_outra_seq;

    if ((bot1 && atual_seq == s2) || (bot2 && atual_seq == s1)) {
        if (atual_seq == s1) {
            outra_seq = s2;
            len_outra_seq = len_s2;
        } else {
            outra_seq = s1;
            len_outra_seq = len_s1;
        }

        for (int i = 0; i < len_outra_seq; i++) {
            if (outra_seq[i] >= atual_dig) {
                atual_seq = outra_seq;
                len_atual_seq = len_outra_seq;
                atual_dig = outra_seq[i];
                break;
            }
        }
    }
}

int main() {
    // Inicialização
    atual_seq = s1;
    len_atual_seq = len_s1;
    atual_dig = s1[0];

    float porc_pot = 0.2; // 20%
    int min_v = 100;
    int max_v = 500;

    while (1) {
        clock_t start_time_loop1 = clock();
        float t_troca = porc_pot * (max_v - min_v) + min_v;

        while (((float)(clock() - start_time_loop1) / CLOCKS_PER_SEC * 1000) < t_troca) {
            loop1(true, false);

            // Impressão dos dígitos do número atual
            if (atual_dig < 10) {
                printf("%d\n", 0); // primeiro dígito
                printf("%d\n", atual_dig); // segundo dígito
            } else {
                printf("%d\n", atual_dig / 10); // primeiro dígito
                printf("%d\n", atual_dig % 10); // segundo dígito
            }

            usleep(100000); // 0.1 segundo = 100ms
        }
    }

    return 0;
}
