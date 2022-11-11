
#include "p30f4013.h"
#include <stdlib.h>
#include <stdio.h>
#include "system.h"
#include <math.h>


_FOSC(CSW_FSCM_OFF & XT_PLL8);
_FWDT(WDT_OFF);                 
_FBORPOR(MCLR_EN & PWRT_OFF);   
_FGS(CODE_PROT_OFF);


extern Delay5us(int);			// Temporisation multiple de "5µs"
extern Delay5ms(int);			// Temporisation multiple de "5ms"
int delayDisplay = 40;
int sensLED = -1;               // sens = -1 -> rien, init, sens = 0 -> vers la gauche, sens = 1 -> vers la droite
int PRI = 60000;                //Register every 20ms

void init(void)
{   
    // Led bargraph ¨port F
    TRISF = 0x00;
    LATF = 0x00;
    
    // Led bargraph port B
    TRISB = 0x00;
    LATB = 0x00;
    PORTF = 0x00;
    PORTB = 0x00;
    
}


void init_Timer(void)
{
    T1CONbits.TON = 1;      //Activate the timer module
    T1CONbits.TCKPS = 2;  
}


void Interrupt_Init(void)
{
    IEC1bits.INT1IE = 1;
    IEC0bits.INT0IE = 1;
    IFS0bits.T1IF = 0;
    IEC0bits.T1IE = 1;
    IPC0bits.T1IP = 1;
}


void initLEDBeforeChaser(void)
{
    PORTBbits.RB1 = 1;
    Delay5ms(400);
    PORTBbits.RB1 = 0;
}


int checkWhichPushButtons(void)
{
    if(!(PORTDbits.RD8 == 0)){      // Si S6 push -> à droite
        PORTBbits.RB1 = 1;
        return 1;
    }
    else if(!(PORTAbits.RA11 == 0)){    // Si S5 push -> à gauche
        PORTBbits.RB0 = 1;
        return 0;
    }else{
        return -1;
    }
    
}

void chaser(void)            
{
    int i;
    
    if(sensLED == 0)
    {
        for(i=0; i<=4;i++){
            LATF = pow(2,i);
            Delay5ms(delayDisplay);
        }
        for(i=8; i<=13;i++){
            LATB = pow(2,i);
            Delay5ms(delayDisplay);
        }
    }else if(sensLED == 1)
    {
        for(i=12; i>=7;i--){
            LATB = pow(2, i);
            Delay5ms(delayDisplay);
    }
        for(i=4; i>=-1;i--){
            LATF = pow(2, i);
            Delay5ms(delayDisplay);
    } 
        
    }
     
}



// Function prototype for timer 1
void __attribute__((__interrupt__, __auto_psv__))_T1Interrupt(void);
void __attribute__((__interrupt__, __auto_psv__))_INT1Interrupt(void);
void __attribute__((__interrupt__, __auto_psv__))_INT0Interrupt(void);



void __attribute__((__interrupt__, __auto_psv__))_T1Interrupt(void)
{
    PORTBbits.RB1 = !PORTBbits.RB1;
    IFS0bits.T1IF = 0;
}


void __attribute__((__interrupt__, __auto_psv__))_INT0Interrupt(void)
{
    
    // Toggle LED RB0 on
    PORTBbits.RB0 = 1;
    
    Delay5ms(10);
    // Toggle LED RB0 off
    PORTBbits.RB0 = 0;
    
    // On change le sens
    sensLED = 0;
    
    IFS0bits.INT0IF=0;
}

void __attribute__((__interrupt__, __auto_psv__))_INT1Interrupt(void)
{
    // Toggle LED RB0 off
    PORTBbits.RB0 = 1;
    
    Delay5ms(10);
    // Toggle LED RB0 ON
    PORTBbits.RB0 = 0;
    
    // On change le sens
    sensLED = 1;
    
    IFS1bits.INT1IF=0;
}

int main (void)
{

    init();
    initLEDBeforeChaser();
    init_Timer();
    Interrupt_Init();
    
    
    while (1)              				//Main Loop of Code Executes forever
    {
        chaser();
        //test();

    } 
	return 0;               			//Code never reaches here!
}





//END of program

