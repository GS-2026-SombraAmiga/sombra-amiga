# Cybersecurity: plano da missão técnica

Como a equipe interpreta cada item da missão técnica (slides 28 e 29 do Kick Off) e o que será construído para atendê-lo.

| O que o slide diz | Pontos | Interpretação | O que vamos construir |
|---|---|---|---|
| "Configurar novas regras no motor de parsing para detectar dados sensíveis (CPF, saúde, senhas)" | 3,0 | Analisar o código e achar onde há dados pessoais | Regras em arquivo de configuração, por nome de campo e por padrão de valor |
| "Rastrear o fluxo das informações coletadas e bloquear vazamentos em saídas inseguras" | 3,0 | Seguir o dado da entrada até uma saída perigosa | Mapa de entradas, saídas e tratamentos, com falha da verificação quando houver vazamento |
| "Utilizar o LLM para traduzir falhas técnicas em alertas claros de risco real ao cidadão" | 2,0 | Explicar a falha em linguagem simples | Chamada a um LLM com texto padrão de reserva quando estiver sem acesso |
| "Dashboard Executivo (Risco Cidadão)" | 2,0 | Painel com um indicador único | Página com nota de 0 a 100, falhas por gravidade e alertas traduzidos |

## Entrega (arquivo ZIP)

- **Código do novo módulo:** o código com as regras de PII.
- **Auditoria do protótipo:** evidências do Taint Analysis em ação.
- **Dashboard atualizado:** vídeo com a atividade e print do painel com o indicador.

## Como funcionaria no Sombra Amiga

A API já recebe dados que justificam a análise: CPF, condição de saúde e contato do familiar. Ainda não há login, então senha só entra se a autenticação for implementada.

1. **Entradas:** dados que chegam nos DTOs da API em C#.
2. **Saídas inseguras:** logs, `Console.WriteLine`, mensagens de erro e respostas da API.
3. **Tratamentos aceitos:** funções de mascaramento ou hash.
4. **Exemplo de falha:** um CPF gravado em log sem máscara.
5. **Alerta traduzido:** "O CPF de um idoso pode ser lido por quem acessa os registros do sistema."

Para mostrar a ferramenta em ação, a auditoria usa um exemplo de vazamento identificado como proposital, com o resultado antes e depois da correção.

## Decisões técnicas propostas

- Ferramenta em Python, na pasta `cyber/`, com análise de arquivos C#.
- Análise simples, dentro de cada método. O objetivo é funcionar bem em poucos casos.
- Risco Cidadão: soma de sensibilidade do dado × exposição da saída, normalizada de 0 a 100. A fórmula é definida pela equipe e documentada.

## Ponto de partida

A ferramenta é construída do zero, na pasta `cyber/`, e analisa o código do próprio protótipo do Sombra Amiga.
