import type { NivelRisco } from './api';

// Paleta de alto contraste: o publico principal sao idosos, muitas vezes no sol.
export const cores = {
  fundo: '#FFFFFF',
  cartao: '#F3F4F6',
  borda: '#9CA3AF',
  texto: '#111111',
  textoSuave: '#374151',
  primaria: '#0B4F8A',
  sucesso: '#166534',
  perigo: '#991B1B',
  avisoFundo: '#FEF3C7',
  avisoTexto: '#78350F',
  erroFundo: '#FEE2E2',
  sucessoFundo: '#DCFCE7',
} as const;

// Fontes grandes por padrao; o app respeita o tamanho de fonte do sistema.
export const fontes = {
  pequena: 17,
  normal: 20,
  destaque: 24,
  titulo: 28,
  enorme: 36,
} as const;

export const espaco = { p: 8, m: 16, g: 24 } as const;

// Cada nivel tem cor E texto: a informacao nunca depende so da cor.
export const coresNivel: Record<NivelRisco, { fundo: string; texto: string }> = {
  Baixo: { fundo: '#166534', texto: '#FFFFFF' },
  Atencao: { fundo: '#FACC15', texto: '#111111' },
  Alto: { fundo: '#C2410C', texto: '#FFFFFF' },
  Extremo: { fundo: '#991B1B', texto: '#FFFFFF' },
};
