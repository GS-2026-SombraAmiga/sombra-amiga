// Sombra Amiga - estacao de monitoramento do ponto de hidratacao (ESP32)
//
// Mede temperatura e umidade (DHT22), calcula a sensacao termica, mostra o nivel
// de risco no display e nos LEDs, toca o buzzer no nivel extremo e envia a leitura
// para a API principal do Sombra Amiga (POST /api/leituras).
// O aviso local funciona mesmo sem rede: quem passa pelo ponto ve o risco na hora.

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "DHTesp.h"

// ---------------- Configuracao ----------------
// Endereco publico da API principal. Troque pelo endereco que o atalho
// iniciar-tunel-esp32.cmd mostrar (https://....trycloudflare.com).
const char* API_URL = "https://COLE-O-ENDERECO-AQUI.trycloudflare.com";

// Ponto de hidratacao onde esta estacao esta instalada (Bebedouro da UBS, simulado).
const char* PONTO_ID = "22222222-2222-2222-2222-222222222222";

const char* WIFI_REDE = "Wokwi-GUEST";  // rede aberta do simulador Wokwi
const char* WIFI_SENHA = "";

const int PINO_DHT = 15;
const int PINO_LED_VERDE = 25;
const int PINO_LED_AMARELO = 26;
const int PINO_LED_VERMELHO = 27;
const int PINO_BUZZER = 14;

const unsigned long INTERVALO_LEITURA_MS = 2000;   // nova leitura do sensor
const unsigned long INTERVALO_ENVIO_MS = 30000;    // envio periodico para a API
const unsigned long INTERVALO_BIPE_MS = 60000;     // bipe repetido no nivel extremo

// Faixas de sensacao termica, iguais as da API principal (base: NWS).
const float LIMITE_ATENCAO = 27.0;
const float LIMITE_ALTO = 32.0;
const float LIMITE_EXTREMO = 41.0;

// ---------------- Estado ----------------
enum Nivel { BAIXO, ATENCAO, ALTO, EXTREMO, SEM_NIVEL };

LiquidCrystal_I2C lcd(0x27, 16, 2);
DHTesp dht;

Nivel nivelAtual = SEM_NIVEL;
unsigned long ultimaLeitura = 0;
unsigned long ultimoEnvio = 0;
unsigned long ultimoBipe = 0;
bool envioPendente = true;  // leitura ainda nao entregue a API (ex.: Wi-Fi conectando)
String statusRede = "Conectando...";

// ---------------- Regras ----------------

// Indice de calor pela formula de Rothfusz (NWS), a mesma da API e do notebook de ML.
float indiceCalor(float temperaturaC, float umidade) {
  float t = temperaturaC * 9.0 / 5.0 + 32.0;
  float r = umidade;
  float f;
  if (t >= 80.0) {
    f = -42.379 + 2.04901523 * t + 10.14333127 * r - 0.22475541 * t * r
        - 6.83783e-3 * t * t - 5.481717e-2 * r * r + 1.22874e-3 * t * t * r
        + 8.5282e-4 * t * r * r - 1.99e-6 * t * t * r * r;
  } else {
    f = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + r * 0.094);
  }
  return (f - 32.0) * 5.0 / 9.0;
}

Nivel classificar(float indice) {
  if (indice >= LIMITE_EXTREMO) return EXTREMO;
  if (indice >= LIMITE_ALTO) return ALTO;
  if (indice >= LIMITE_ATENCAO) return ATENCAO;
  return BAIXO;
}

const char* nomeNivel(Nivel n) {
  switch (n) {
    case BAIXO: return "BAIXO";
    case ATENCAO: return "ATENCAO";
    case ALTO: return "ALTO";
    case EXTREMO: return "EXTREMO";
    default: return "";
  }
}

// ---------------- Saidas locais ----------------

void escreverLinha(int linha, const String& texto) {
  String t = texto;
  while (t.length() < 16) t += ' ';
  lcd.setCursor(0, linha);
  lcd.print(t.substring(0, 16));
}

// Verde: baixo. Amarelo: atencao. Vermelho: alto e extremo.
void acenderLeds(Nivel n) {
  digitalWrite(PINO_LED_VERDE, n == BAIXO);
  digitalWrite(PINO_LED_AMARELO, n == ATENCAO);
  digitalWrite(PINO_LED_VERMELHO, n == ALTO || n == EXTREMO);
}

void bipar(int vezes) {
  for (int i = 0; i < vezes; i++) {
    tone(PINO_BUZZER, 1000, 100);
    delay(200);
  }
  noTone(PINO_BUZZER);
}

// ---------------- Rede ----------------

void enviarLeitura(float temperaturaC, float umidade) {
  if (WiFi.status() != WL_CONNECTED) {
    // Sem Wi-Fi a leitura fica pendente e sai assim que a rede conectar.
    statusRede = millis() < 15000 ? "Conectando..." : "SEM REDE";
    envioPendente = true;
    return;
  }
  ultimoEnvio = millis();
  envioPendente = false;

  String url = String(API_URL) + "/api/leituras";
  String corpo = String("{\"pontoId\":\"") + PONTO_ID + "\",\"temperaturaC\":" + String(temperaturaC, 1)
                 + ",\"umidadePct\":" + String(umidade, 1) + "}";

  HTTPClient http;
  WiFiClientSecure clienteSeguro;
  WiFiClient cliente;
  if (url.startsWith("https")) {
    // Prototipo: aceita o certificado do tunel sem validar a cadeia.
    clienteSeguro.setInsecure();
    http.begin(clienteSeguro, url);
  } else {
    http.begin(cliente, url);
  }
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");

  int codigo = http.POST(corpo);
  if (codigo == 201) {
    statusRede = "API: enviado";
  } else if (codigo < 0) {
    statusRede = "SEM REDE";
  } else {
    statusRede = String("API: erro ") + codigo;
  }
  Serial.printf("POST %s -> %d\n", url.c_str(), codigo);
  http.end();
}

// ---------------- Ciclo principal ----------------

void lerSensor() {
  TempAndHumidity leitura = dht.getTempAndHumidity();

  if (dht.getStatus() != 0 || isnan(leitura.temperature) || isnan(leitura.humidity)) {
    // Falha do sensor: avisa no ponto e nao envia dado errado para a API.
    nivelAtual = SEM_NIVEL;
    acenderLeds(SEM_NIVEL);
    escreverLinha(0, "ERRO SENSOR");
    escreverLinha(1, "Verifique o DHT");
    Serial.println("Falha na leitura do DHT22");
    return;
  }

  float indice = indiceCalor(leitura.temperature, leitura.humidity);
  Nivel nivel = classificar(indice);
  bool mudouNivel = nivel != nivelAtual;
  nivelAtual = nivel;

  acenderLeds(nivel);
  escreverLinha(0, String(indice, 1) + (char)223 + "C " + nomeNivel(nivel));

  // Envia na hora quando o nivel muda ou quando havia leitura pendente; fora isso, a cada 30 segundos.
  if (mudouNivel || envioPendente || millis() - ultimoEnvio >= INTERVALO_ENVIO_MS) {
    if (WiFi.status() == WL_CONNECTED) escreverLinha(1, "Enviando...");
    enviarLeitura(leitura.temperature, leitura.humidity);
  }
  escreverLinha(1, statusRede);

  Serial.printf("T=%.1fC U=%.0f%% Sensacao=%.1fC Nivel=%s Rede=%s\n",
                leitura.temperature, leitura.humidity, indice, nomeNivel(nivel), statusRede.c_str());

  // No nivel extremo, o buzzer chama a atencao de quem passa pelo ponto.
  if (nivel == EXTREMO && (mudouNivel || millis() - ultimoBipe >= INTERVALO_BIPE_MS)) {
    ultimoBipe = millis();
    bipar(2);
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(PINO_LED_VERDE, OUTPUT);
  pinMode(PINO_LED_AMARELO, OUTPUT);
  pinMode(PINO_LED_VERMELHO, OUTPUT);
  pinMode(PINO_BUZZER, OUTPUT);

  lcd.init();
  lcd.backlight();
  escreverLinha(0, "Sombra Amiga");
  escreverLinha(1, "Iniciando...");

  dht.setup(PINO_DHT, DHTesp::DHT22);

  // Conexao sem bloquear: o aviso local comeca mesmo se a rede demorar.
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_REDE, WIFI_SENHA, 6);
}

void loop() {
  if (millis() - ultimaLeitura >= INTERVALO_LEITURA_MS) {
    ultimaLeitura = millis();
    lerSensor();
  }
  delay(10);
}
