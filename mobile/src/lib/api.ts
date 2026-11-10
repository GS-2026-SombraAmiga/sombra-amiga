// Cliente da API principal do Sombra Amiga (C#). Os tipos espelham as respostas
// documentadas no Swagger: campos em camelCase e enums como texto.

export type Perfil = 'Idoso' | 'TrabalhadorDeRua';
export type NivelRisco = 'Baixo' | 'Atencao' | 'Alto' | 'Extremo';
export type StatusCheckIn = 'EstouBem' | 'PrecisoDeAjuda';
export type TipoPonto = 'Sombra' | 'Agua' | 'SombraEAgua';

export interface Cidadao {
  id: string;
  nome: string;
  cpfMascarado: string;
  perfil: Perfil;
  temCondicaoSaude: boolean;
}

export interface DadosCadastro {
  perfil: Perfil;
  nome: string;
  cpf: string;
  contatoFamiliar: string;
  condicaoSaude?: string;
  ocupacao?: string;
}

export interface RiscoAtual {
  indiceCalorC: number | null;
  nivel: NivelRisco | null;
  orientacao: string;
}

export interface Ponto {
  id: string;
  nome: string;
  tipo: TipoPonto;
  latitude: number;
  longitude: number;
  distanciaKm: number | null;
}

export interface Alerta {
  id: string;
  nivel: NivelRisco;
  origem: 'Sensor' | 'Previsao';
  mensagem: string;
  pontoId: string | null;
  criadoEmUtc: string;
  ativo: boolean;
}

export interface CheckIn {
  id: string;
  cidadaoId: string;
  status: StatusCheckIn;
  dataHoraUtc: string;
}

export class ErroApi extends Error {
  constructor(
    mensagem: string,
    readonly status?: number,
    readonly semConexao = false,
  ) {
    super(mensagem);
  }
}

const TEMPO_LIMITE_MS = 8000;

async function chamar<T>(base: string, caminho: string, init?: RequestInit): Promise<T> {
  const controle = new AbortController();
  const limite = setTimeout(() => controle.abort(), TEMPO_LIMITE_MS);
  let resposta: Response;
  try {
    resposta = await fetch(`${base.replace(/\/$/, '')}${caminho}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      signal: controle.signal,
    });
  } catch {
    throw new ErroApi('Sem conexão com o servidor.', undefined, true);
  } finally {
    clearTimeout(limite);
  }

  if (!resposta.ok) {
    throw new ErroApi(await mensagemDeErro(resposta), resposta.status);
  }
  if (resposta.status === 204) {
    return undefined as T;
  }
  return (await resposta.json()) as T;
}

// A API devolve erros como ProblemDetails: {"title": "CPF inválido.", "status": 400}.
// Erros de validação automática vêm em inglês, então trocamos por uma mensagem simples.
async function mensagemDeErro(resposta: Response): Promise<string> {
  try {
    const corpo = (await resposta.json()) as { title?: string; errors?: unknown };
    if (corpo.errors) return 'Confira os dados informados.';
    if (corpo.title) return corpo.title;
  } catch {
    // corpo vazio ou fora do formato esperado
  }
  return 'Não foi possível concluir agora. Tente de novo.';
}

export const api = {
  cadastrar: (base: string, dados: DadosCadastro) =>
    chamar<Cidadao>(base, '/api/cidadaos', { method: 'POST', body: JSON.stringify(dados) }),

  excluirCadastro: (base: string, id: string) =>
    chamar<void>(base, `/api/cidadaos/${id}`, { method: 'DELETE' }),

  risco: (base: string, cidadaoId: string) =>
    chamar<RiscoAtual>(base, `/api/risco/atual?cidadaoId=${encodeURIComponent(cidadaoId)}`),

  checkIn: (base: string, cidadaoId: string, status: StatusCheckIn) =>
    chamar<CheckIn>(base, '/api/checkins', { method: 'POST', body: JSON.stringify({ cidadaoId, status }) }),

  pontosProximos: (base: string, latitude: number, longitude: number, raioKm: number) =>
    chamar<Ponto[]>(base, `/api/pontos/proximos?latitude=${latitude}&longitude=${longitude}&raioKm=${raioKm}`),

  alertasAtivos: (base: string) => chamar<Alerta[]>(base, '/api/alertas/ativos'),

  testarConexao: (base: string) => chamar<Ponto[]>(base, '/api/pontos'),
};
