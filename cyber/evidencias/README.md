# Auditoria do protótipo: Taint Analysis em ação

Evidências geradas por `python gerar_evidencias.py --sem-llm`, na pasta `cyber/`, em 16/11/2026. Sem credencial da API do Claude nesta máquina, os alertas usam o texto de reserva das regras.

## Resumo

| Análise | Risco Cidadão | Vazamentos | Resultado do `--bloquear` | Painel |
|---|---|---|---|---|
| Protótipo Sombra Amiga (API C#, serviço Java e testes) | **30, Moderado** | 0 | Liberado (código 0) | [print](painel-prototipo-sombra-amiga.png) |
| Exemplo com vazamento (proposital) | **100, Crítico** | 6 | **Bloqueado** (código 1) | [print](painel-exemplo-com-vazamento.png) |
| Exemplo corrigido | **0, Baixo** | 0 | Liberado (código 0) | [print](painel-exemplo-corrigido.png) |

O painel interativo, com as três análises em abas, é o [painel-risco-cidadao.html](painel-risco-cidadao.html). As saídas do terminal estão nos arquivos `terminal-*.txt`, e o detalhe de cada análise está nos arquivos `.md` e `.json`.

## 1. Protótipo real

Foram 101 arquivos analisados e 163 métodos seguidos pelo Taint Analysis.

**Nenhum dado pessoal chega a uma saída insegura.** A API já foi construída com essa proteção:
- o CPF é um tipo próprio cujo `ToString()` devolve o valor mascarado;
- as respostas usam DTOs que expõem só o `CpfMascarado` e um `TemCondicaoSaude` (sim ou não);
- os logs da integração com a Rede de Apoio não carregam dados pessoais;
- para a Rede de Apoio, a API envia só o `cidadaoId`.

Os 18 achados são estáticos:

| Gravidade | Quantidade | O que é | Leitura da equipe |
|---|---|---|---|
| Média | 4 | Chave de serviço, senha do banco e segredo do JWT com **valor padrão de desenvolvimento** (`appsettings.json` e `application.properties`) | **Achado real.** Os valores podem ser trocados por variável de ambiente, mas, se alguém publicar o sistema sem trocá-los, a chave e o segredo ficam conhecidos, porque o repositório é público. **Correção recomendada:** em produção, tornar essas variáveis obrigatórias, sem valor padrão. |
| Baixa | 9 | CPFs **fictícios** nos testes da API (ex.: `529.982.247-25`, número de exemplo conhecido) | Esperado: dados de teste. A ferramenta só aponta CPFs com dígitos verificadores válidos. |
| Baixa | 4 | E-mails fictícios nos testes do serviço Java | Esperado: dados de teste. |
| Baixa | 1 | Segredo fictício num teste do serviço Java | Esperado: dado de teste. |

## 2. Antes e depois: exemplo com vazamentos propositais

O arquivo [exemplos/com-vazamento/ServicoCadastroInseguro.cs](../exemplos/com-vazamento/ServicoCadastroInseguro.cs) tem seis falhas **escritas de propósito**, e a Sentinela encontrou as seis:

| # | Dado | Saída | Gravidade | Linha |
|---|---|---|---|---|
| 1 | CPF | Resposta da API (`Results.Ok`) | Crítica (5 × 5) | 26 |
| 2 | CPF | Mensagem de erro (`throw new ConflitoException($"O CPF {dados.Cpf} ...")`) | Crítica (5 × 4) | 20 |
| 3 | CPF | Log | Alta (5 × 3) | 12 |
| 4 | Saúde | Console, **depois de passar pela variável `resumo`** (linha 15 → linha 16) | Alta (5 × 3) | 16 |
| 5 | Senha | Log (o parâmetro `senha` é a fonte) | Alta (5 × 3) | 32 |
| 6 | Contato da família | Envio a outro sistema (`PostAsJsonAsync`) | Alta (3 × 4) | 23 |

A falha 4 mostra o rastreamento: a condição de saúde entra em `resumo`, numa string interpolada, e só depois chega ao `Console.WriteLine`. O relatório mostra esse caminho linha a linha.

Com `--bloquear`, a execução termina com **código 1**, e no GitHub Actions isso barra a entrega ([.github/workflows/sentinela.yml](../../.github/workflows/sentinela.yml)).

A versão [corrigida](../exemplos/corrigido/ServicoCadastroSeguro.cs):
- mascara o CPF no log e na resposta;
- registra só *se* há condição de saúde, não qual é;
- tira o dado da mensagem de erro;
- não grava a senha no log;
- envia um identificador em vez do telefone.

O resultado cai para **0 achados e Risco Cidadão 0**.

## Testes da ferramenta

São 18 testes automatizados, todos passando (`python -m unittest discover -s testes -v`). Eles cobrem:
- regras de PII e validação de CPF;
- rastreamento por variável;
- sanitizadores e derivações seguras;
- strings fixas que só mencionam a palavra "CPF";
- código Java;
- segredos de configuração;
- o índice de Risco Cidadão.

## Falsos positivos corrigidos durante a construção

Na primeira execução no protótipo real, a ferramenta apontou três "vazamentos" que **não eram reais**:
1. o cadastro de cidadão, que responde com o `CidadaoResposta`, que mascara o CPF;
2. o cadastro de ponto de hidratação, cuja localização é de um lugar público;
3. o login do serviço Java, que devolve só o token.

**Causa:** a contaminação passava pelo retorno de construtores e métodos de negócio (`new DadosCadastro(..., cpf)` contaminava o objeto inteiro).

**Correção:** a contaminação passou a seguir só as operações que montam texto a partir do dado (`Format`, `Concat`, `Trim`...). Isso está documentado nas regras (`chamadas_que_propagam`) e coberto por dois testes novos.

O mesmo cuidado eliminou um falso positivo de segredo (`CHAVE_SERVICO = "chave-servico"`, que é o *nome* de um esquema no Swagger) e ajustou o índice. Com o expoente 2, os 13 dados fictícios de teste somados levavam o protótipo a "Crítico", o que não refletia o risco real. Com o expoente 3, falhas leves quase não pesam.
