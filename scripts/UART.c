#include "p30f4013.h"
#include <stdlib.h>
#include <stdio.h>
#include "system.h"
#include <math.h>
#include <string.h>

          

//Function:UART2Init : init UART module
void UART2Init(void)
{
    U2MODE = 0;
    U2STA = 0;
    U2BRG = BRGVAL;         // set baudrate to 9600 (dans system.h)
    
    U2MODEbits.PDSEL = 0;   //Enable UART for 8-bit data,  no parity
    U2MODEbits.STSEL = 0;   //1 STOP bit,

    U2MODEbits.UARTEN = 1;  //UART pins are controlled by UART as defined by UEN<1:0> and UTXEN control bits
    U2MODEbits.ALTIO = 1;   //UART Alternate I/O Selection bit (ici UART communicates using UxATX and UxARX I/O pins)
    U2STAbits.UTXEN = 1;    //Enable transmit

    //Initialize UART with receive interrupt
    U2STAbits.URXISEL = 1;
    IEC1bits.U2RXIE = 1;        //Enable receive interrupt
    IFS1bits.U2RXIF = 0;
    
    
    //Initialize UART with transmit interrupt
    U2STAbits.UTXISEL = 1;      //Transmission Interrupt Mode Selection bit (1 : avec RAZ, 0 : sans RAZ)
    IEC1bits.U2TXIE = 0;        //Enable transmit interrupt
    IFS1bits.U2TXIF = 0;
    
    //Initialize valeur register � 0
    U2TXREG = 0;
    U2RXREG = 0;
}


// Function:UART2PutChar - This routine writes a character to the transmit FIFO
void UART2PutChar( unsigned char ch )
{
    while(U2STAbits.TRMT == 0);	// wait for transmit ready
    U2TXREG = ch;				// transmit character
}


void UART2ShowString(char *string)
{
    int index = 0;
    
    while(string[index]){
        UART2PutChar(string[index]);
        index ++;
    }
}