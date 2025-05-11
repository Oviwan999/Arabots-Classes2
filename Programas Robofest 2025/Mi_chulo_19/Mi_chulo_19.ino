#define pwmD 13
#define pwmI 10
#define SDL 27
#define SDA 23
#define SDB 29
#define SDE 31
#define SIB 33 
#define SIL 35
#define SIA 25
#define SR  39

void setup() {
// put your setup code here, to run once:


//Motores
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);

//PWM
  pinMode(pwmD, OUTPUT);
  pinMode(pwmI, OUTPUT);

//sensores 
  pinMode(27, INPUT);
  pinMode(23, INPUT);
  pinMode(29, INPUT);
  pinMode(31, INPUT);
  pinMode(33, INPUT);
  pinMode(35, INPUT);
  pinMode(25, INPUT);
  pinMode(39, OUTPUT);

  analogWrite(pwmD, 0);
  analogWrite(pwmI, 0);

  digitalWrite(8, HIGH);
  digitalWrite(9, HIGH);
  digitalWrite(11, HIGH);
  digitalWrite(12, HIGH);



   while(digitalRead(33) == 1){

  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  digitalWrite(11, LOW);
  digitalWrite(12, LOW);

  } 

  delay(3000);

digitalWrite(SR, HIGH); //pone el pin en estado 1 (5V)


//reto sorpesa

} 

void loop() {

//sensor derecho abajo

  if (digitalRead(SDA) == 1){
  
  analogWrite(pwmD, 255);
  analogWrite(pwmI, 255);

  digitalWrite(8, LOW);
  digitalWrite(9, HIGH);
  digitalWrite(11, LOW);
  digitalWrite(12, HIGH);
  delay(570);

  digitalWrite(8, HIGH);
  digitalWrite(9, LOW);
  digitalWrite(11, LOW);
  digitalWrite(12, HIGH);
  delay(570);
 

//sensor izquierdo abajo

} else if (digitalRead(SIA) == 1){ 

  analogWrite(pwmD, 255);
  analogWrite(pwmI, 255);

  digitalWrite(8, LOW);
  digitalWrite(9, HIGH);
  digitalWrite(11, LOW);
  digitalWrite(12, HIGH);
  delay(570);

  digitalWrite(8, LOW);
  digitalWrite(9, HIGH);
  digitalWrite(11, HIGH);
  digitalWrite(12, LOW);
  delay(570);

//sensor izquierdo lado

} else if (digitalRead (SIL) == 0){


  analogWrite(pwmD, 255);
  analogWrite(pwmI, 255);

  digitalWrite(8, HIGH);
  digitalWrite(9, LOW);
  digitalWrite(11, LOW);
  digitalWrite(12, HIGH);
  delay(500);

  digitalWrite(8,  HIGH);
  digitalWrite(9,  LOW);
  digitalWrite(11, HIGH);
  digitalWrite(12, LOW );
  delay(100);

  //sensor derecho lado 
  
}   else if (digitalRead (SDL) == 0){

  analogWrite(pwmD, 255);
  analogWrite(pwmI, 255);

  digitalWrite(8, LOW);
  digitalWrite(9, HIGH);
  digitalWrite(11, HIGH);
  digitalWrite(12, LOW);
  delay(850);

  digitalWrite(8,  HIGH);
  digitalWrite(9,  LOW);
  digitalWrite(11, HIGH);
  digitalWrite(12, LOW );
  delay(100);
 
 //sensor derecho barrera 

 } else if (digitalRead (SDB) == 0){

  analogWrite(pwmD, 255);
  analogWrite(pwmI, 255);

  digitalWrite(8, LOW);
  digitalWrite(9, HIGH);
  digitalWrite(11, HIGH);
  digitalWrite(12, LOW);
  delay(200);

  digitalWrite(8,  HIGH);
  digitalWrite(9,  LOW);
  digitalWrite(11, HIGH);
  digitalWrite(12, LOW );
  delay(250);  

  //sensor izquierdo barrera

 } else if (digitalRead (SIB) == 0){

  analogWrite(pwmD, 255);
  analogWrite(pwmI, 255);

  digitalWrite(8, HIGH);
  digitalWrite(9, LOW);
  digitalWrite(11, LOW);
  digitalWrite(12, HIGH);
  delay(200);

  digitalWrite(8,  HIGH);
  digitalWrite(9,  LOW);
  digitalWrite(11, HIGH);
  digitalWrite(12, LOW );
  delay(250);
  
  }else {
  // put your main code here, to run repeatedly:

analogWrite(pwmD, 255);
analogWrite(pwmI, 255);

digitalWrite(8, HIGH);
digitalWrite(9, LOW);
digitalWrite(11, HIGH);
digitalWrite(12, LOW);
delay(10);
}

 
}