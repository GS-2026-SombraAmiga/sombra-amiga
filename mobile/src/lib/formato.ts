import type { NivelRisco, TipoPonto } from './api';

export function nomeNivel(nivel: NivelRisco): string {
  return { Baixo: 'baixo', Atencao: 'atenção', Alto: 'alto', Extremo: 'extremo' }[nivel];
}

export function nomeTipoPonto(tipo: TipoPonto): string {
  return { Sombra: 'Sombra', Agua: 'Água', SombraEAgua: 'Sombra e água' }[tipo];
}

function doisDigitos(n: number): string {
  return n.toString().padStart(2, '0');
}

// Formatacao manual, sem depender do suporte a Intl do aparelho.
export function hora(dataIso: string | Date): string {
  const d = typeof dataIso === 'string' ? new Date(dataIso) : dataIso;
  return `${doisDigitos(d.getHours())}:${doisDigitos(d.getMinutes())}`;
}

export function dataHora(dataIso: string | Date): string {
  const d = typeof dataIso === 'string' ? new Date(dataIso) : dataIso;
  return `${doisDigitos(d.getDate())}/${doisDigitos(d.getMonth() + 1)} às ${hora(d)}`;
}

export function temperatura(celsius: number): string {
  return `${celsius.toFixed(1).replace('.', ',')} °C`;
}

export function distancia(km: number): string {
  if (km < 1) return `${Math.round((km * 1000) / 10) * 10} m`;
  return `${km.toFixed(1).replace('.', ',')} km`;
}

export function mascararCpfDigitado(texto: string): string {
  const d = texto.replace(/\D/g, '').slice(0, 11);
  return d
    .replace(/^(\d{3})(\d)/, '$1.$2')
    .replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/\.(\d{3})(\d)/, '.$1-$2');
}

export function primeiroNome(nome: string): string {
  return nome.trim().split(/\s+/)[0] ?? nome;
}
