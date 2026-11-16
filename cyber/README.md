# Sentinela Cidadã: privacidade do cidadão no código da Sombra Amiga

Parte da CitizenTech **Sombra Amiga** na disciplina **Cybersecurity**.

**Integrantes:** Glauco Heitor Gonçalves (RM 555978) e Pedro Henrique Junqueira (RM 556278).

**Vídeo de demonstração:** _(link)_

A Sombra Amiga guarda dados delicados de quem ela protege: o **CPF**, a **condição de saúde** e o **contato da família** de idosos e trabalhadores de rua. A Sentinela Cidadã é uma ferramenta de análise estática, feita do zero em Python sem dependências obrigatórias, que:

1. **Encontra dados pessoais (PII)** no código C# e Java e na configuração, com regras num arquivo editável.
2. **Rastreia o caminho de cada dado (Taint Analysis)**, da entrada até logs, console, mensagens de erro, arquivos, respostas da API e envios a outros sistemas, e **bloqueia a entrega** quando um dado chega a uma dessas saídas sem proteção.
3. **Traduz cada falha técnica num alerta claro** de risco real ao cidadão, usando um LLM (Claude), com texto de reserva quando o LLM não está disponível.
4. **Resume tudo no painel de Risco Cidadão**, um índice de 0 a 100.

| Item da missão | Pontos | Onde está |
|---|---|---|
| Novas regras para detectar dados sensíveis (CPF, saúde, senhas) | 3,0 | [regras/regras_pii.toml](regras/regras_pii.toml) e [sentinela/regras.py](sentinela/regras.py) |
| Rastrear o fluxo das informações e bloquear vazamentos em saídas inseguras | 3,0 | [regras/saidas.toml](regras/saidas.toml), [sentinela/analisador.py](sentinela/analisador.py) e o workflow [sentinela.yml](../.github/workflows/sentinela.yml) |
| LLM traduzindo falhas técnicas em alertas de risco ao cidadão | 2,0 | [sentinela/llm.py](sentinela/llm.py) |
| Dashboard executivo de Risco Cidadão | 2,0 | [sentinela/painel.py](sentinela/painel.py) e [evidencias/painel-risco-cidadao.html](evidencias/painel-risco-cidadao.html) |

## Como rodar

Precisa só do Python 3.11 ou mais novo. Na pasta `cyber/`:

```bash
# Analisa o protótipo real (API em C#, serviço Java e testes)
python -m sentinela analisar ../api/src ../servico-soa/src ../api/tests --nome "Protótipo Sombra Amiga" --saida saida --bloquear

# Demonstração: um serviço com vazamentos propositais e a versão corrigida
python -m sentinela analisar exemplos/com-vazamento --nome "Exemplo com vazamento" --saida saida --bloquear
python -m sentinela analisar exemplos/corrigido --nome "Exemplo corrigido" --saida saida --bloquear

# Painel com as três análises
python -m sentinela painel saida/prototipo-sombra-amiga.json saida/exemplo-com-vazamento.json saida/exemplo-corrigido.json --saida saida/painel.html

# Testes da ferramenta
python -m unittest discover -s testes -v
```

- **Saída de cada análise:** `<nome>.json` (dados do painel) e `<nome>.md` (relatório legível).
- **Com `--bloquear`:** o comando termina com código 1 quando há vazamento de gravidade alta ou crítica. É assim que o GitHub Actions barra a entrega (veja [.github/workflows/sentinela.yml](../.github/workflows/sentinela.yml)).

**Alertas pelo LLM:** instale o SDK oficial (`pip install anthropic`) e configure uma credencial da API do Claude (`ANTHROPIC_API_KEY`). O modelo padrão é o `claude-opus-5-5`; outro pode ser escolhido em `SENTINELA_MODELO`. Sem o SDK ou sem a credencial, ou com `--sem-llm`, cada alerta usa o texto de reserva da categoria, e o relatório informa qual das duas fontes gerou cada alerta.

## 1. Regras de dados sensíveis (PII)

As regras ficam em [regras/regras_pii.toml](regras/regras_pii.toml). Para criar uma regra nova, basta copiar um bloco; o código não muda.

| Categoria | Sensibilidade | Nomes reconhecidos (exemplos) | Valores reconhecidos |
|---|---|---|---|
| CPF | 5 | `cpf`, `CpfNumero`, `documento` | `529.982.247-25` e 11 dígitos, **só se os dígitos verificadores conferirem** |
| Dado de saúde | 5 | `condicaoSaude`, `diagnostico`, `medicamento` | |
| Senha ou segredo | 5 | `senha`, `password`, `secret`, `token`, `chave` | |
| Contato pessoal | 3 | `contatoFamiliar`, `telefone`, `email` | `(11) 91234-5678`, e-mails |
| Localização | 3 | `latitude`, `endereco`, `cep` | |

Também estão nas regras:
- **Nomes que indicam dado já protegido:** `CpfMascarado`, `SenhaHash` e `TemCondicaoSaude` não são tratados como dado sensível.
- **Sanitizadores:** `Mascarar(...)`, `.Mascarado`, `Hash(...)` e `Anonimizar(...)`.
- **Derivações seguras:** `!IsNullOrWhiteSpace(saude)` diz *se* o dado existe, sem carregá-lo adiante.

**Varreduras feitas:**
1. **Inventário:** onde cada dado pessoal é declarado no código.
2. **Dados escritos no código:** um CPF válido ou um e-mail escrito direto em código ou teste.
3. **Segredos na configuração:** `.json`, `.properties` e `.yml`.
   - Um valor que só vem de variável de ambiente (`${JWT_SECRET}`) é correto e não gera achado.
   - Um valor padrão de desenvolvimento (`${JWT_SECRET:segredo-dev}`) tem peso menor.
   - Uma senha fixa tem peso maior.

## 2. Taint Analysis

O analisador segue cada dado pessoal dentro de cada método, em C# e Java:

1. **Fontes:**
   - parâmetros com nome sensível (`string senha`);
   - acessos a membros sensíveis (`dados.Cpf`, `cidadao.CondicaoSaude`).
2. **Propagação:** `var texto = $"... {dados.CondicaoSaude}"` contamina `texto`, e `var copia = texto` contamina `copia`. Reatribuir um valor limpo descontamina.
3. **Proteção:** o que passa por um sanitizador deixa de ser perigoso (`Mascarar(dados.Cpf)`).
4. **Saídas inseguras ([regras/saidas.toml](regras/saidas.toml)):**

   | Saída | Exposição | Exemplos |
   |---|---|---|
   | Log | 3 | `log.LogInformation`, `logger.info` |
   | Console | 3 | `Console.WriteLine`, `System.out.println` |
   | Exceção | 4 | `throw new ...Exception(...)` |
   | Arquivo | 4 | `File.WriteAllText`, `Files.write` |
   | Envio a outro sistema | 4 | `PostAsJsonAsync` |
   | Resposta da API | 5 | `return Ok(...)`, `ResponseEntity.ok(...)` |

Um dado sensível que chega a uma saída sem proteção vira um **vazamento**. O relatório mostra o caminho completo, da linha de origem à linha da saída.

- **Peso de cada achado:** sensibilidade do dado × exposição da saída, de 1 a 25.
- **Gravidade:** crítica a partir de 20, alta a partir de 12, média a partir de 6 e baixa abaixo disso.
- **Bloqueio:** vazamentos de gravidade alta ou crítica bloqueiam a entrega.

**Limitações conhecidas:** a análise é intraprocedural, ou seja, segue o dado dentro de cada método e não entre métodos. Ela também reconhece o código por padrões de texto, sem compilá-lo. Um objeto inteiro devolvido pela API (`return Ok(cidadao)`) só é detectado se o membro sensível aparecer no trecho. Na API da Sombra Amiga isso já é evitado pelos DTOs de resposta, que expõem só o `CpfMascarado`.

## 3. Alertas para o cidadão (LLM)

Para cada tipo de achado, [sentinela/llm.py](sentinela/llm.py) envia ao Claude a descrição técnica (dado, saída, arquivo, trecho e caminho) com uma instrução fixa: escrever em português simples, em até duas frases, qual dado fica exposto, quem poderia vê-lo e que mal isso causa, sem inventar fatos.

- **Chamadas e falhas:** achados iguais reaproveitam o mesmo alerta. Se a chamada falha ou o modelo se recusa a responder, o texto de reserva da regra é usado.
- **Exemplo de saída:** _"O CPF de um cidadão atendido pela Sombra Amiga pode ser lido por quem consegue ver os registros (logs) do sistema. Com o CPF, alguém pode se passar por essa pessoa em cadastros e golpes."_

## 4. Índice de Risco Cidadão

```
Risco Cidadão = 100 × (1 − Π(1 − (peso / 25)³))
```

- **Probabilidade de dano:** cada achado tem uma chance estimada de causar dano, p = (peso/25)³:
  - um CPF devolvido pela API (5 × 5) vale p = 1;
  - um CPF no log (5 × 3) vale p = 0,22;
  - um segredo de desenvolvimento no repositório (5 × 2) vale p = 0,06;
  - um CPF fictício num teste (5 × 1) vale p = 0,008.
- **Leitura do índice:** é a chance de pelo menos um achado causar dano. Ele cresce a cada falha e nunca passa de 100. O cubo faz poucas falhas graves pesarem muito mais que muitas falhas leves, então dados fictícios de teste não inflam o índice.
- **Faixas:** baixo de 0 a 29, moderado de 30 a 59, alto de 60 a 84 e crítico de 85 a 100.

O painel ([sentinela/painel.py](sentinela/painel.py)) é uma página HTML única, sem bibliotecas, com tema claro e escuro. Ele mostra:
- o índice e a faixa;
- as falhas por gravidade;
- os alertas para o cidadão;
- o detalhe técnico de cada achado;
- o inventário de dados pessoais.

Quando recebe várias análises, ele as mostra em abas, para comparar o antes e o depois.

## Auditoria do protótipo (evidências)

| Arquivo | Conteúdo |
|---|---|
| [evidencias/painel-risco-cidadao.html](evidencias/painel-risco-cidadao.html) | Painel com as três análises |
| [evidencias/](evidencias) | Prints do painel, relatórios em JSON e Markdown, e as saídas do terminal |

Os resultados e a leitura de cada análise estão em [evidencias/README.md](evidencias/README.md).

## Estrutura

```
cyber/
├── regras/            regras de PII (regras_pii.toml) e saídas inseguras (saidas.toml)
├── sentinela/         a ferramenta: regras, analisador (PII + Taint), risco, llm, relatorio, painel, CLI
├── exemplos/          serviço com vazamentos propositais e a versão corrigida (não compilados)
├── testes/            testes automatizados (unittest)
└── evidencias/        relatórios, painel e prints da auditoria
```
