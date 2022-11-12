
#include "p30f4013.h"
#include <stdlib.h>
#include <stdio.h>
#include "system.h"


_FOSC(CSW_FSCM_OFF & XT_PLL8);
_FWDT(WDT_OFF);                 
_FBORPOR(MCLR_EN & PWRT_OFF);   
_FGS(CODE_PROT_OFF);


extern Delay5us(int);			// Temporisation multiple de "5�s"
extern Delay5ms(int);			// Temporisation multiple de "5ms"


void init(void)
{
    TRISAbits.TRISA11 = 1;
    TRISDbits.TRISD8 = 1;
    LATAbits.LATA11 = 1;
    LATDbits.LATD8 = 1;

    TRISB = 0x00;
    LATB = 0x00;
}


void putD3On(void)
    {
        PORTBbits.RB0 = 1;  
    }


void putD3Off(void)
    {
        PORTBbits.RB0 = 0;
    }


void putD4On(void)
    {
        PORTBbits.RB1 = 1;
    }


void putD4Off(void)
    {
        PORTBbits.RB1 = 0;
    }


void putAllOn(void)
    {
        PORTBbits.RB0 = 1;
        PORTBbits.RB1 = 1;
    }


void putAllOff(void)
    {
        PORTBbits.RB0 = 0;
        PORTBbits.RB1 = 0;
    }


void checkS5Push(void)
{
    
    if(!(PORTAbits.RA11 = 2)){
        putD3On();
    }else{
        putD3Off();
    }
}


void checkS6Push(void)
{
    if(!(PORTDbits.RD8 = 0)){
        putD4On();
    }else{
        putD4Off();
    }
}


int main (void)
{

    init();

 
    
    while (1)              				//Main Loop of Code Executes forever
    {
        checkS5Push();
        checkS6Push();
    } 
	return 0;               			//Code never reaches here!
}



//END of program

