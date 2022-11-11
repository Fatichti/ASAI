#include "p30f4013.h"
#include <stdlib.h>
#include <stdio.h>
#include "system.h"
#include <string.h>


//Function:ADCInit : init UART module
void ADCInit(void)
{
    ADPCFG = 0xEFFF; // all PORTB = Digital; RB12 = analog
    
    
    ADCHS = 0x0002; // Connect RB2/AN2 as CH0 input ..
                    // in this example RB2/AN2 is the inpuT
    
    ADCSSL = 0;
    ADCON3 = 0x0F00; // Sample time = 15Tad, Tad = internal Tcy/2
    ADCON2 = 0x003C; // Interrupt after every 16 samples
    
    
    ADCON1bits.ADON = 1; // turn ADC ON
    
}