
#include "p30f4013.h"
#include <stdlib.h>
#include <stdio.h>
#include "system.h"


extern Delay5us(int);			// Temporisation multiple de "5µs"
extern Delay5ms(int);			// Temporisation multiple de "5ms"
int Counter = 0;

void init(void)
{
    TRISAbits.TRISA11 = 1;
    TRISDbits.TRISD8 = 1;
    LATAbits.LATA11 = 1;
    LATDbits.LATD8 = 1;
    
    // Led bargraph ¨port F
    TRISF =0x00;
    LATF = 0x00;
}


void checkS5Push(void)
{
    
    if((PORTAbits.RA11 == 0) && (Counter <16)){
        Counter ++;
        PORTF = Counter;
        Delay5ms(50);
        
    }
}

void checkS6Push(void)
{
    if((PORTDbits.RD8 == 0) && (Counter >0)){
        Counter --;
        PORTF = Counter;
        Delay5ms(50);
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

