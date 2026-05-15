/*
 * PRUEBA DE BUCLE DE RETORNO (LOOPBACK)
 * Puenta con un cable el Pin 11 con el Pin 2
 */

volatile unsigned long contador = 0;
unsigned long tiempoAnterior = 0;

void setup() {

  // --- GENERADOR 40kHz (Pin 11) ---
  pinMode(11, OUTPUT);
  TCCR1A = _BV(COM1A0);              
  TCCR1B = _BV(WGM12) | _BV(CS10);   
  OCR1A = 198;                       


}

void loop() {

  
}