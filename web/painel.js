// Painel web do Sombra Amiga: alertas ativos, situacao dos pontos e indicador de impacto.
// Atualiza sozinho e, se a API cair, mantem os ultimos dados na tela com um aviso.
// Todo texto vindo da API entra como textContent, nunca como HTML.

const config = window.SOMBRA_AMIGA_CONFIG || {};
const parametros = new URLSearchParams(window.location.search);
const API = (parametros.get('api') || config.apiUrl || '').replace(/\/$/, '');
const INTERVALO_MS = (config.intervaloSegundos || 30) * 1000;
const JANELA_LEITURA_MS = 3 * 60 * 60 * 1000; // o risco considera as leituras das ultimas 3 horas

const NOMES_NIVEL = { Baixo: 'Baixo', Atencao: 'Atenção', Alto: 'Alto', Extremo: 'Extremo' };
const NOMES_TIPO = { Sombra: 'Sombra', Agua: 'Água', SombraEAgua: 'Sombra e água' };

let ultimaAtualizacao = null;

const $ = (id) => document.getElementById(id);

function elemento(tag, classe, texto) {
  const el = document.createElement(tag);
  if (classe) el.className = classe;
  if (texto !== undefined) el.textContent = texto;
  return el;
}

function hora(data) {
  return new Date(data).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function dataHora(data) {
  return new Date(data).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function dataIsoLocal(data) {
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, '0');
  const dia = String(data.getDate()).padStart(2, '0');
  return `${ano}-${mes}-${dia}`;
}

function etiquetaNivel(nivel) {
  return elemento('span', `etiqueta nivel-${nivel.toLowerCase()}`, NOMES_NIVEL[nivel] ?? nivel);
}

async function buscar(caminho) {
  const resposta = await fetch(API + caminho, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(8000),
  });
  if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
  return resposta.json();
}

function desenharAlertas(alertas) {
  const lista = $('alertas');
  lista.replaceChildren();
  $('totalAlertas').textContent = alertas.length;

  if (alertas.length === 0) {
    lista.append(elemento('li', 'vazio', 'Nenhum alerta de calor ativo.'));
    return;
  }

  // Previsao do dia seguinte primeiro, depois as medicoes, das mais novas para as mais antigas.
  const ordenados = [...alertas].sort((a, b) =>
    a.origem !== b.origem ? (a.origem === 'Previsao' ? -1 : 1) : b.criadoEmUtc.localeCompare(a.criadoEmUtc));

  for (const alerta of ordenados) {
    const item = elemento('li', 'alerta');
    const cabecalho = elemento('div', 'alerta-cabecalho');
    cabecalho.append(
      etiquetaNivel(alerta.nivel),
      elemento('span', 'origem', alerta.origem === 'Previsao' ? 'Previsão para amanhã' : 'Medido no ponto'),
      elemento('span', 'quando', `desde ${dataHora(alerta.criadoEmUtc)}`),
    );
    item.append(cabecalho, elemento('p', 'mensagem', alerta.mensagem));
    lista.append(item);
  }
}

function desenharPontos(pontos, leituras) {
  const corpo = $('pontos');
  corpo.replaceChildren();
  let emRisco = 0;

  pontos.forEach((ponto, i) => {
    const leitura = leituras[i];
    const recente = leitura && Date.now() - new Date(leitura.dataHoraUtc).getTime() <= JANELA_LEITURA_MS;
    if (recente && (leitura.nivel === 'Alto' || leitura.nivel === 'Extremo')) emRisco++;

    const linha = elemento('tr');
    const celulaNivel = elemento('td');
    celulaNivel.append(recente ? etiquetaNivel(leitura.nivel) : elemento('span', 'etiqueta sem-leitura', 'Sem leitura recente'));

    linha.append(
      elemento('th', null, ponto.nome),
      elemento('td', null, NOMES_TIPO[ponto.tipo] ?? ponto.tipo),
      elemento('td', null, leitura ? `${leitura.indiceCalorC.toFixed(1).replace('.', ',')} °C` : '–'),
      celulaNivel,
      elemento('td', null, leitura ? dataHora(leitura.dataHoraUtc) : 'Nunca'),
    );
    linha.firstChild.scope = 'row';
    corpo.append(linha);
  });

  $('pontosEmRisco').textContent = emRisco;
}

function desenharImpacto(impacto) {
  $('percentual').textContent = impacto.checkInsEsperados === 0
    ? 'Sem dias de alerta'
    : `${impacto.percentualConfirmado.toLocaleString('pt-BR')}%`;
  $('detalheImpacto').textContent =
    `${impacto.checkInsConfirmados} de ${impacto.checkInsEsperados} esperados em ${impacto.diasComAlerta} dia(s) com alerta`;
}

async function atualizar() {
  try {
    const hoje = new Date();
    const inicio = new Date(hoje);
    inicio.setDate(hoje.getDate() - 6);

    const [alertas, pontos, impacto] = await Promise.all([
      buscar('/api/alertas/ativos'),
      buscar('/api/pontos'),
      buscar(`/api/indicadores/impacto?inicio=${dataIsoLocal(inicio)}&fim=${dataIsoLocal(hoje)}`),
    ]);
    const leituras = await Promise.all(
      pontos.map((p) => buscar(`/api/leituras?pontoId=${encodeURIComponent(p.id)}&limite=1`).then((l) => l[0])),
    );

    desenharAlertas(alertas);
    desenharPontos(pontos, leituras);
    desenharImpacto(impacto);

    ultimaAtualizacao = new Date();
    $('aviso').hidden = true;
    $('atualizacao').textContent =
      `Atualizado às ${hora(ultimaAtualizacao)} · atualiza a cada ${INTERVALO_MS / 1000} s`;
  } catch (erro) {
    const quando = ultimaAtualizacao ? ` Mostrando os dados de ${hora(ultimaAtualizacao)}.` : '';
    $('aviso').textContent = `Os dados estão indisponíveis: não foi possível falar com a API.${quando}`;
    $('aviso').hidden = false;
    $('atualizacao').textContent = 'Tentando de novo...';
    console.warn('Falha ao atualizar o painel:', erro);
  }
}

if (API) {
  $('linkSwagger').href = `${API}/swagger`;
}
atualizar();
setInterval(atualizar, INTERVALO_MS);
