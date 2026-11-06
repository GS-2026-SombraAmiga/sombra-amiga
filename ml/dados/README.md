# Dados de ML

| Item | Valor |
|---|---|
| Fonte | INMET, dados históricos de estações automáticas |
| Link | https://portal.inmet.gov.br/dadoshistoricos |
| Estação | São Paulo, Mirante de Santana (A701) |
| Coordenadas | -23,496 / -46,620, altitude 785,64 m |
| Período | 01/01/2015 a 31/10/2026, dados horários |
| Pasta | `a701/`, 12 arquivos CSV (9,2 MB) |

`brutos/` guarda os arquivos de todas as estações (4,6 GB) e fica fora do Git.

## Qualidade dos dados

- Cobertura de temperatura e umidade acima de 97% em todos os anos.
- 4.293 dos 4.323 dias têm pelo menos 20 horas de leitura. Os demais são descartados.
- Radiação só existe durante o dia, cerca de 53% das horas.

## Cuidados no carregamento

Tratados em [preparar_dados.py](../preparar_dados.py):

- O formato muda entre os anos: data, hora e marcador de ausência (`-9999` ou vazio).
- A hora vem em **UTC** e é convertida para horário local (UTC-3). O pico diário de temperatura cai entre 14h e 15h locais, o que confirma a conversão.
