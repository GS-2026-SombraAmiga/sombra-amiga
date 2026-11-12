# Estação de monitoramento no ponto (ESP32 / Wokwi)

Parte da CitizenTech **Sombra Amiga** na disciplina **Physical Computing: IOT & IOB**.

**Integrantes:** Glauco Heitor Gonçalves (RM 555978) e Pedro Henrique Junqueira (RM 556278).

## Por que um circuito no ponto de hidratação

O app avisa quem tem celular e internet, mas nem todo mundo que passa pela praça tem os dois. A estação no ponto de hidratação resolve isso de duas formas:

1. **Avisa ali mesmo**, com display, luzes e som, quem passa pelo ponto.
2. **Alimenta o sistema:** envia a leitura para a API principal, que calcula o risco mostrado no app, abre os alertas e alimenta o indicador de impacto.

Ela é a fonte dos dados de "Calor agora" do app.

## Comportamento

A cada 2 segundos, o ESP32 lê temperatura e umidade no DHT22 e calcula a **sensação térmica** pela fórmula de Rothfusz (NWS), a mesma da API e do notebook de ML.

| Sensação térmica | Nível | LED | Buzzer |
|---|---|---|---|
| abaixo de 27 °C | BAIXO | verde | silêncio |
| de 27 °C a 32 °C | ATENCAO | amarelo | silêncio |
| de 32 °C a 41 °C | ALTO | vermelho | silêncio |
| 41 °C ou mais | EXTREMO | vermelho | 3 bipes, repetidos a cada 10 s |

**Display:**
- **Linha 1:** sensação e nível, por exemplo `48.6°C EXTREMO`.
- **Linha 2:** situação do envio: `API: enviado`, `SEM REDE` ou `API: erro 404`.

**Envio:** `POST /api/leituras` com o ponto, a temperatura e a umidade. Envia na hora quando o nível muda e, fora isso, a cada 30 segundos.

**Falhas:**
- **Sem rede:** o aviso local continua funcionando, e o display indica `SEM REDE`.
- **Falha do sensor:** o display mostra `ERRO SENSOR`, e nada é enviado à API.

## Circuito

| Componente | Pino do ESP32 | Observação |
|---|---|---|
| DHT22 (dados) | D15 | Alimentação em 3V3 |
| LCD 16x2 I2C (SDA / SCL) | D21 / D22 | Endereço 0x27, alimentação em VIN |
| LED verde | D25 | Resistor de 220 Ω |
| LED amarelo | D26 | Resistor de 220 Ω |
| LED vermelho | D27 | Resistor de 220 Ω |
| Buzzer | D14 | |

| Arquivo | Conteúdo |
|---|---|
| [sketch.ino](sketch.ino) | Código do ESP32 |
| [diagram.json](diagram.json) | Circuito no formato do Wokwi |
| [libraries.txt](libraries.txt) | Bibliotecas: DHT sensor library for ESPx e LiquidCrystal I2C |
| [integrantes.txt](integrantes.txt) | Nomes dos integrantes, pedido na entrega |

## Como rodar no Wokwi

1. Em [wokwi.com](https://wokwi.com), entre na sua conta e crie um projeto **ESP32**.
2. Substitua o conteúdo de `sketch.ino` e `diagram.json` pelo deste repositório.
3. Crie o arquivo `libraries.txt` (no Wokwi: seta ao lado das abas > New file) e cole o conteúdo.
4. Clique em **Play**. Para mudar a temperatura e a umidade, clique no DHT22 durante a simulação.

**Para enviar as leituras para a API:**

1. Rode a API com o `iniciar-demo.cmd`, na raiz do repositório.
2. Rode o `iniciar-tunel-esp32.cmd`, também na raiz. Ele mostra um endereço `https://....trycloudflare.com`.
3. Cole esse endereço na constante `API_URL` do `sketch.ino` no Wokwi e rode de novo.

O Wokwi roda na nuvem e não enxerga o seu computador. A forma oficial de conectar os dois, o Private IoT Gateway, é paga. Por isso o projeto usa um túnel temporário do Cloudflare, sem conta.

**Atenção:** enquanto o túnel estiver aberto, qualquer pessoa com o endereço consegue usar a API. Use-o só durante a demonstração, com dados fictícios, e feche a janela ao terminar. O endereço muda a cada uso.

## Testes (Azure DevOps, Feature F-13)

| Test Case | Como reproduzir |
|---|---|
| TC-13.01 Nível extremo | DHT22 em 38 °C e 50%: o display mostra cerca de `48.6°C EXTREMO`, o LED vermelho acende, o buzzer toca e a leitura aparece na API |
| TC-13.02 Nível baixo | DHT22 em 22 °C e 50%: o display mostra `BAIXO`, o LED verde acende e o buzzer fica em silêncio |
| TC-13.03 Sem rede | Sem túnel, ou com o endereço antigo: o display mostra `EXTREMO` e `SEM REDE`, e as luzes e o buzzer continuam funcionando |

## Limitações do protótipo

- O ESP32 aceita o certificado HTTPS do túnel sem validar a cadeia (`setInsecure`).
- Não há autenticação do sensor na API.
- Em produção, cada estação teria sua própria chave, e a API ficaria em um servidor público.
