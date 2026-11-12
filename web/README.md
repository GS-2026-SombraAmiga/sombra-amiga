# Painel web

Painel de acompanhamento para a UBS ou a ONG parceira do **Sombra Amiga**. É a aplicação web que a VM Linux hospeda, na disciplina Operating Systems.

**Integrantes:** Glauco Heitor Gonçalves (RM 555978) e Pedro Henrique Junqueira (RM 556278).

## O que mostra

| Bloco | Conteúdo |
|---|---|
| Resumo | Alertas ativos, pontos em risco alto ou extremo e o indicador de impacto (check-ins confirmados em dias de alerta, últimos 7 dias) |
| Alertas ativos | Previsão do modelo de ML e medições dos sensores, com nível e horário |
| Pontos de sombra e água | Última leitura de cada ponto. Leituras com mais de 3 horas aparecem como "Sem leitura recente" |

O painel se atualiza sozinho a cada 30 segundos. Se a API cair, ele mantém os últimos dados na tela e mostra o aviso "Os dados estão indisponíveis".

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| [index.html](index.html) | Estrutura da página |
| [painel.js](painel.js) | Busca os dados na API e monta a tela. O texto vindo da API nunca é tratado como HTML |
| [estilo.css](estilo.css) | Visual, com o nível sempre escrito além da cor |
| [config.js](config.js) | Endereço da API e intervalo de atualização |

São arquivos estáticos, sem etapa de compilação. Na VM, o nginx serve o painel e encaminha `/api` para a API principal.

## Como testar fora da VM

Com a API rodando na porta 5080:

```bash
cd web
python -m http.server 8090
```

Abra `http://localhost:8090/?api=http://127.0.0.1:5080`.

## Testes (Azure DevOps, Feature F-14)

| Test Case | Resultado |
|---|---|
| TC-14.01 Exibir alerta novo no painel | Uma leitura de calor extremo no Abrigo do Terminal apareceu na lista em até 30 segundos, sem recarregar a página |
| TC-14.02 Avisar indisponibilidade da API | Com a API inacessível, o painel mostrou o aviso e continuou tentando, sem ficar em branco |
