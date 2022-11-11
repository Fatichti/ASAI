
#include "p30f4013.h"
#include <stdlib.h>
#include <stdio.h>
#include "system.h"
#include <math.h>
#include <string.h>


_FOSC(CSW_FSCM_OFF & XT_PLL8);
_FWDT(WDT_OFF);                 
_FBORPOR(MCLR_EN & PWRT_OFF);   
_FGS(CODE_PROT_OFF);


extern void Delay5us(int);			// Temporisation multiple de "5�s"
extern void Delay5ms(int);			// Temporisation multiple de "5ms"


// Fonction init de UART.c
extern void UART2Init(void);
extern char UART2IsPressed(void);
extern char UART2GetChar(void);
extern void UART2PutChar(char);
extern void UART2ShowString(char);

// Fonction LED de LEC.c
extern void d3flash(int);           // Flash LED D3 en ms

int received;                       //Var pour check si on recoit une touche clavier
int data;

void init(void)
{      
    // Led bargraph port B
    TRISB = 0x00;
    LATB = 0x00;
    PORTF = 0x00;
    PORTB = 0x00;
 }


//Lorsque l'on appui sur une touche du clavier, une interrumption se fait, on sauvegarde la valeur dans le register pour faire un echo
void __attribute__((__interrupt__))_U2RXInterrupt(void)
{
    received = 1;
    data = U2RXREG;
    IFS1bits.U2RXIF = 0;   
}

void printWelcomeMessageUART(void)
{
    unsigned int i,  data[]={0x4845,0x4c4c,0x4f0a,0x0d00};      //Envoyer message Hello
    
    for(i=0;i<sizeof(data)/sizeof(unsigned int);i++)
    {
		UART2PutChar((unsigned char)(data[i]>>8));  // send most significant byte
		UART2PutChar((unsigned char) data[i]);         // send least significant byte
	}
}


void showInfoSelectLed(void)
{
    UART2ShowString("\n\n\rChoisir un num�ro de LED � afficher :\n\r- 3 : LED D3\n\r- 4 : LED D4\n\n\rChoix : ");
}

void selectLed(char *numLED)
{
    TRISB = 0x00;
    LATB = 0x00;
    Delay5ms(100);
    
    if(numLED == '3')
    {
        UART2ShowString("\n\rAllumage LED 3");
        Delay5ms(200);
        PORTBbits.RB0 = 1;
        Delay5ms(200);
        PORTBbits.RB0 = 0;
    }
    else if(numLED == '4')
    {
        UART2ShowString("\n\rAllumage LED 4");
        Delay5ms(200);
        PORTBbits.RB1 = 1;
        Delay5ms(200);
        PORTBbits.RB1 = 0;
    }else
    {
        UART2ShowString("\n\rErreur : num�ro de LED incorrect (valeur possible : 3 ou 4), veuillez ressayer.");
    }
    showInfoSelectLed();
}



int main (void)
{
    //init();
    received=0;
    
    // On init UART :
    UART2Init();

    // On flash une LED pour dire que tout est initialis�
    //d3flash(2000);
    
    // On affiche un message de bienvenue en UART
    //printWelcomeMessageUART();
    UART2ShowString("\rBienvenu,\n\n\rR�gles d'utilisation : \n\rChoisir un num�ro de LED � afficher :\n\r- 3 : LED D3\n\r- 4 : LED D4\n\n\rChoix : ");
    
    while (1)              				//Main Loop of Code Executes forever
    {
        if(received==1){
            //UART2PutChar(data);
            //U2TXREG = data;
            selectLed(data);
            received=0;
        }
    } 
	return 0;               			//Code never reaches here!
}





//END of program


