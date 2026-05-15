/*
 * VERIFICADOR DE 40kHz - ARDUINO NANO
 * Lee la señal generada externamente por el Pin D2.
 */

volatile unsigned long contadorPulsos = 0;
unsigned long tiempoAnterior = 0;
const long intervalo = 1000; // Medir cada 1 segundo

// Función rápida de conteo
void conteo() {
  contadorPulsos++;
}

void setup() {
  Serial.begin(115200); // Asegúrate de poner esta velocidad en el monitor
  
  pinMode(2, INPUT); // Pin D2 como entrada
  
  // Configurar interrupción en el Pin 2 (D2)
  attachInterrupt(digitalPinToInterrupt(2), conteo, RISING);

  Serial.println("========================================");
  Serial.println("    NANO: MODO ESCUCHA (40 kHz)        ");
  Serial.println("========================================");
}

void loop() {
  unsigned long tiempoActual = millis();

  if (tiempoActual - tiempoAnterior >= intervalo) {
    // Pausa temporal de interrupciones para lectura limpia
    noInterrupts();
    unsigned long totalPulsos = contadorPulsos;
    contadorPulsos = 0;
    interrupts();

    float frecuenciaKHz = totalPulsos / 1000.0;

    Serial.print("Frecuencia detectada: ");
    Serial.print(frecuenciaKHz, 2);
    Serial.print(" kHz");

    // Diagnóstico rápido
    if (frecuenciaKHz == 0) {
      Serial.println(" -> [!] Sin señal detectada.");
    } else if (frecuenciaKHz >= 38.0 && frecuenciaKHz <= 42.0) {
      Serial.println(" -> [OK] ¡SEÑAL DE BATALLA DETECTADA!");
    } else {
      Serial.println(" -> [?] Frecuencia fuera de rango.");
    }

    tiempoAnterior = tiempoActual;
  }
}