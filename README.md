# Sombra Amiga

CitizenTech da Global Solution 2026.2, FIAP, Engenharia de Software, 3º ano.

**Integrantes**

- Glauco Heitor Gonçalves, RM 555978
- Pedro Henrique Junqueira, RM 556278

## Ficha da CitizenTech

| Campo | Conteúdo |
|---|---|
| **Nome** | Sombra Amiga |
| **Cidade e bairro** | São Paulo, Brasilândia (zona norte) |
| **Cidadão beneficiado** | Idosos e trabalhadores de rua expostos ao calor extremo |
| **Problema, em uma frase** | Nos dias de calor extremo, idosos e trabalhadores de rua não sabem a tempo que correm risco nem onde encontrar sombra e água por perto. |
| **Como funciona** | Sensores nos pontos de hidratação medem o calor, um modelo prevê o risco do dia seguinte, e o app avisa o cidadão, mostra os pontos próximos e permite um check-in "estou bem" para um familiar acompanhar. |
| **O que cada parte faz** | Ver a tabela abaixo |
| **Link do repositório** | https://github.com/GS-2026-SombraAmiga/sombra-amiga |
| **Indicador de impacto** | Percentual de check-ins confirmados em dias de alerta |
| **ODS conectados** | 3 (saúde e bem-estar), 10 (redução das desigualdades), 11 (cidades sustentáveis), 13 (ação contra a mudança do clima) |

## Partes da solução

| Pasta | Parte | Disciplina |
|---|---|---|
| [api/](api/) | API principal em C# | C# Software Development |
| [servico-soa/](servico-soa/) | Rede de Apoio, serviço Java (Spring Boot) | SOA e Web Services |
| [mobile/](mobile/) | App do cidadão (Expo, React Native) | Mobile Development & IOT |
| [web/](web/) | Painel web | Operating Systems (aplicação hospedada) |
| [iot/](iot/) | Estação de monitoramento no ponto (ESP32, Wokwi) | Physical Computing |
| [ml/](ml/) | Previsão de risco de calor | IA & Machine Learning |
| [infra/](infra/) | Provisionamento Linux | Operating Systems |
| [cyber/](cyber/) | PII, Taint Analysis, Risco Cidadão | Cybersecurity |
| [docs/](docs/) | Pesquisa, evidências, plano de Cybersecurity e Testing | Todas |

## Pesquisa sobre o cidadão

A proposta se baseia em dados e estudos públicos e em personas **simuladas**. Nenhuma pessoa real foi entrevistada. Detalhes em [docs/pesquisa-cidadao.md](docs/pesquisa-cidadao.md).

## Dados

Nenhum dado pessoal real é usado. Os dados de pessoas são simulados, e os dados de ML são públicos, com a fonte descrita em [ml/dados/README.md](ml/dados/README.md).
