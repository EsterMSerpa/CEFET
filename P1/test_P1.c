// Microprocessadores II

#include <avr/io.h>
#include <avr/interrupt.h>

#define F_CPU 4000000
#include <util/delay.h>

void setup_hard (void);

void setup (void);
void loop (void);

void f_rtos (void);
void loop1 (void);
void loop2 (void);
void loop3 (void);
void loop4 (void);

void loop_INT0 (void);
void loop_INT1 (void);

unsigned char decod_7seg (unsigned char dado);
void maq_display (void);

void analogWrite(unsigned char canal, unsigned char dc);
void conv_digito (unsigned int dado);

unsigned char mem_display[4] = {0,1,2,3};
unsigned char mem_display_dp[4] = {0,0,0,0};

unsigned int max1, max2, max3, max4;

#define display PORTB  // 0 .. 7
#define en_disp PORTC  // 0 .. 3

unsigned char flag_pd = 0;

ISR(INT0_vect) {

    loop_INT0();
}

ISR(INT1_vect) {

    loop_INT1();
}

ISR(TIMER2_COMPA_vect) {

    PIND = 0X80;
    
    f_rtos();
}

int main (void) {
    
    setup_hard();
    
    while(1) loop();
    
    return 0;
    
}


void setup_hard (void) {
    
     cli();
    
    // CONFIG ENTRADAS E SAIDAS
    PORTB = 0X00;  // 0000 0000
    PORTC = 0X00;  // 0000 0000
    PORTD = 0X00;  // 0000 0000
    
    // DEFINE DIREÇÃO DOS PINOS (1 = saída, 0 = entrada)
    DDRB = 0xFF;   // 1111 1111 → Todos os pinos B são SAÍDAS (Display)
    DDRC = 0x0F;   // 0000 1111 → PC0 a PC3 são SAÍDAS (display), PC4 a PC6 são ENTRADAS (potenciometros)
    DDRD = 0xE0;   // 1110 0000 → PD5, PD6, PD7 são SAÍDAS (PWMB, PWMA e sensor); PD0 a PD4 são ENTRADAS (INT0 - D2 e INT1 - D3)
    
    // CONFIG INTERRUPCAO EXTERNA
    EICRA = 0x0A;  // 0000 1010
    EIMSK = 0x03;  // 0000 0011
    EIFR = 0x00;   // 0000 0000
    
    
    // CONFIG TIMER 2 PARA INT 5ms
    //Fpwm = Fosc / (N * 256)  →  N = prescaler
    

    TCCR2A = 0x02;   // WGM21 = 1 (modo CTC - zera ao atingir OCR2A), os outros bits em 0
    TCCR2B = 0x05;   // CS22 = 1, CS21 = 0, CS20 = 1 → prescaler de 128

    TCNT2  = 0;      // Zera o contador do Timer2 (começa a contar do zero)
    OCR2A  = 155;    // Valor de comparação: quando o contador chegar a 155, gera interrupção
    OCR2B  = 0;      // Não usado neste modo, mas zerado por segurança

    TIMSK2 = 0x02;   // Ativa a interrupção por comparação com OCR2A (bit OCIE2A = 1)
    TIFR2  = 0x00;   // Limpa quaisquer flags de interrupção pendentes

    ASSR   = 0x00;   // Timer2 usa o clock interno (não usa oscilador externo)
    GTCCR  = 0x00;   // Desativa funções de controle especial como reset ou sincronismo com outros timers
   
    
    //CONFIG TIMER 0 PWM
    //Fpwm = Fosc / (N * 256)  →  N = prescaler

    TCCR0A = 0xA3;  // 10100011
                    // COM0A1=1, COM0A0=0 → PWM no pino OC0A (modo não-invertido)
                    // COM0B1=1, COM0B0=0 → PWM no pino OC0B (modo não-invertido)
                    // WGM01=1, WGM00=1   → Modo Fast PWM (modo 3: TOP = 0xFF)

    TCCR0B = 0x02;  // 00000010
                    // CS01 = 1 → prescaler = 8
                    // WGM02 = 0 → continua no modo Fast PWM com TOP = 255

    TCNT0  = 0;     // Zera o contador do Timer0
    OCR0A  = 0;     // Valor de comparação A = 0 → duty cycle = 0% no pino OC0A (sem sinal)
    OCR0B  = 0;     // Valor de comparação B = 0 → duty cycle = 0% no pino OC0B (sem sinal)
    TIMSK0 = 0x00;  // Nenhuma interrupção do Timer0 ativada
    TIFR0  = 0x00;  // Limpa quaisquer flags de interrupção pendentes

    
    //CONFIG AD PARA FOSC = 4MHZ
    ADMUX = 0X44; // 0100 0100
    ADCSRA = 0X85; // 1000 0101
    ADCSRB = 0X00; // 0000 0000
    DIDR0 = 0X0F; // 0000 1111
   
}


void f_rtos (void) {

  static unsigned int cont1=0, cont2=0, cont3=0, cont4=0;

  extern unsigned int max1, max2, max3, max4;
  
  maq_display();

  if (cont1<max1) cont1++; else {
    cont1 = 0;
    loop1();
  }

  if (cont2<max2) cont2++; else {
    cont2 = 0;
    loop2();
  }
  
  if (cont3<max3) cont3++; else {
    cont3 = 0;
    loop3();
  }
  
  if (cont4<max4) cont4++; else {
    cont4 = 0;
    loop4();
  }


}

void maq_display (void) {

  static unsigned char estado=0;
  
  unsigned char disp_aux=0;

  
  switch (estado) {

    case 0:
      estado = 1;

      en_disp = en_disp | 0x01;
      
      disp_aux = decod_7seg(mem_display[1]);
      if (mem_display_dp[1]) {
          display = disp_aux | 0x80;
      }
      else {
          display = disp_aux;
      }
      
      en_disp = en_disp & 0xfd;

      break;

    case 1:
      estado = 2;

      en_disp = en_disp | 0x02;
      
      disp_aux = decod_7seg(mem_display[2]);
      if (mem_display_dp[2]) {
          display = disp_aux | 0x80;
      }
      else {
          display = disp_aux;
      }
      
      en_disp = en_disp & 0xfb;
      
      break;

    case 2:
      estado = 3;

      en_disp = en_disp | 0x04;
      
      disp_aux = decod_7seg(mem_display[3]);
      if (mem_display_dp[3]) {
          display = disp_aux | 0x80;
      }
      else {
          display = disp_aux;
      }
      
      en_disp = en_disp & 0xf7;

      break;

    case 3:
      estado = 0;

      en_disp = en_disp | 0x08;
      
      disp_aux = decod_7seg(mem_display[0]);
      if (mem_display_dp[0]) {
          display = disp_aux | 0x80;
      }
      else {
          display = disp_aux;
      }
      
      en_disp = en_disp & 0xfe;
     
      break;

    default: estado = 0;

  }

}

// /////////////////////////////////

unsigned char decod_7seg (unsigned char dado) {
    
    unsigned char valor;

  switch (dado) {
    case  0: valor = 0x3f; break;
    case  1: valor = 0x06; break;
    case  2: valor = 0x5b; break;
    case  3: valor = 0x4f; break;
    case  4: valor = 0x66; break;
    case  5: valor = 0x6d; break;
    case  6: valor = 0x7d; break;
    case  7: valor = 0x07; break;
    case  8: valor = 0x7f; break;
    case  9: valor = 0x6f; break;
    case 10: valor = 0x77; break;
    case 11: valor = 0x7c; break;
    case 12: valor = 0x39; break;
    case 13: valor = 0x5e; break;
    case 14: valor = 0x79; break;
    case 15: valor = 0x71; break;

    default: valor = 0x00; break;
  }
  
  return valor;
  
}

void conv_digito (unsigned int dado) {

  mem_display[3] = dado % 10;
  dado = dado/10;

  mem_display[2] = dado % 10;
  dado = dado/10;

  mem_display[1] = dado % 10;
  dado = dado/10;

  mem_display[0] = dado % 10;

}


void analogWrite(unsigned char canal, unsigned char dc) {
    
    switch (canal) {
        
        case 0:
            OCR0A = dc;
            break;
            
        case 1:
            OCR0B = dc;
            break;
        
    }
    
}

unsigned int analogRead(unsigned char canal) {
    
    unsigned int resultado=0;
    
    if (canal < 16) {
        ADMUX = ADMUX & 0XF0;
        ADMUX = ADMUX | canal;
    }
    
    ADCSRA = ADCSRA | (1<<ADSC);
    
    while (ADCSRA & 0X40);
    
    resultado = ADCH << 8;
    resultado = resultado | ADCL;
    
    return resultado;
    
}

//////////// LOGICA  ////////////////////

// unsigned char decod_7seg (unsigned char dado)
// void conv_digito (unsigned int dado)
// void analogWrite(unsigned char canal, unsigned char dc)
// unsigned int analogRead(unsigned char canal)

// unsigned char mem_display[4] = {0,1,2,3};
// unsigned char mem_display_dp[4] = {0,0,0,0};

unsigned char s1(unsigned char estado);
unsigned char s2(unsigned char estado);

void trata_pot (void);

unsigned char estado, flag_seq, flag_tp;

void setup (void) {
    
 // tempo base de 5ms
    
  max1 = 250 -1;
  max2 = 3 -1;
  max3 = 1000 -1;
  max4 = 1000 -1;
  
  flag_tp = 0;
  
  flag_seq = 0;
  estado = 10;
  
  mem_display[0]=1;
  mem_display[1]=0;
  mem_display_dp[1]=0;
  
  mem_display[2]=255;
  mem_display[3]=255;
        
}

void loop (void) {
    
    if (flag_tp) {
        trata_pot();
        flag_tp=0;
    }
      
}

void loop1 (void) {
    
    if (flag_seq==0) {
        estado = s1(estado);
    }
    else {
        estado = s2(estado);
    }
     
}

void loop2 (void) {
    
    flag_tp=1;
}

void loop3 (void) {
    
}

void loop4 (void) {
    
}

void loop_INT0 (void) {
    
    flag_seq = 0;
    mem_display_dp[1]=0;
     
}

void loop_INT1 (void) {
    
    flag_seq = 1;
    mem_display_dp[1]=1;
       
}

// /////////////////////////////

unsigned char s1(unsigned char estado) {
    
    switch (estado) {
        case 10:
            estado = 11;
            mem_display[0]=1;
            mem_display[1]=1;
            break;
        case 11:
        case 15:
        case 16:
            estado = 17;
            mem_display[0]=1;
            mem_display[1]=7;
            break;
        case 17:
            estado = 12;
            mem_display[0]=1;
            mem_display[1]=2;
            break;
        case 12:
            estado = 20;
            mem_display[0]=2;
            mem_display[1]=0;
            break;
        case 20:
            estado = 19;
            mem_display[0]=1;
            mem_display[1]=9;
            break;
        case 19:
            estado = 18;
            mem_display[0]=1;
            mem_display[1]=8;
            break;
        case 18:
        case 13:
            estado = 14;
            mem_display[0]=1;
            mem_display[1]=4;
            break;
        case 14:
            estado = 10;
            mem_display[0]=1;
            mem_display[1]=0;
            break;
            
        default : 
            estado = 10;
            mem_display[0]=1;
            mem_display[1]=0;
            break;
    }
    
    return estado;
    
}

unsigned char s2(unsigned char estado) {
    
    switch (estado) {
        case 17:
            estado = 12;
            mem_display[0]=1;
            mem_display[1]=2;
            break;
        case 12:
            estado = 18;
            mem_display[0]=1;
            mem_display[1]=8;
            break;
        case 18:
        case 13:
            estado = 14;
            mem_display[0]=1;
            mem_display[1]=4;
            break;
        case 14:
        case 10:
            estado = 11;
            mem_display[0]=1;
            mem_display[1]=1;
            break;
        case 11:
            estado = 19;
            mem_display[0]=1;
            mem_display[1]=9;
            break;
        case 19:
            estado = 16;
            mem_display[0]=1;
            mem_display[1]=6;
            break;
        case 16:
            estado = 15;
            mem_display[0]=1;
            mem_display[1]=5;
            break;
        case 15:
        case 20:
            estado = 17;
            mem_display[0]=1;
            mem_display[1]=7;
            break;
            
        default:
            estado = 17;
            mem_display[0]=1;
            mem_display[1]=7;
            break;
    }
    
    return estado;
    
}


void trata_pot (void) {
    
    unsigned int valor;
    float vl;
    unsigned char dado;
    
    valor = analogRead(4);
    vl = valor/1023.0;
    dado = (unsigned char) 10*vl;
    
    mem_display[3] = dado % 10;
    dado = dado/10;
    mem_display[2] = dado % 10;
    
    max1 = 100 + 300*vl;
    
    _delay_ms(10);
}




