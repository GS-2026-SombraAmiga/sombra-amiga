import { useCallback } from 'react';
import { RefreshControl, ScrollView, Text } from 'react-native';

import { AvisoSemConexao, Cartao, EtiquetaNivel, Mensagem, Paragrafo, estilos } from '@/components/ui';
import { useDadosComCache } from '@/hooks/use-dados-com-cache';
import { api, type Alerta } from '@/lib/api';
import { dataHora } from '@/lib/formato';
import { useSessao } from '@/lib/sessao';

// Previsao do dia seguinte primeiro, depois os alertas dos sensores, do mais novo ao mais antigo.
function ordenar(alertas: Alerta[]): Alerta[] {
  return [...alertas].sort((a, b) => {
    if (a.origem !== b.origem) return a.origem === 'Previsao' ? -1 : 1;
    return b.criadoEmUtc.localeCompare(a.criadoEmUtc);
  });
}

export default function Alertas() {
  const { urlApi } = useSessao();
  const alertas = useDadosComCache('alertas', useCallback(() => api.alertasAtivos(urlApi), [urlApi]));
  const lista = ordenar(alertas.dados ?? []);

  return (
    <ScrollView
      contentContainerStyle={estilos.tela}
      refreshControl={<RefreshControl refreshing={alertas.carregando && alertas.dados !== null} onRefresh={alertas.recarregar} />}>
      {alertas.semConexao ? <AvisoSemConexao atualizadoEm={alertas.atualizadoEm} /> : null}
      {alertas.erro ? <Mensagem tipo="erro" texto={alertas.erro} /> : null}

      {lista.map((a) => (
        <Cartao key={a.id}>
          <EtiquetaNivel nivel={a.nivel} />
          <Text style={[estilos.secao, { marginTop: 0 }]}>
            {a.origem === 'Previsao' ? 'Previsão para amanhã' : 'Medido em um ponto de hidratação'}
          </Text>
          <Paragrafo>{a.mensagem}</Paragrafo>
          <Paragrafo suave>Emitido em {dataHora(a.criadoEmUtc)}</Paragrafo>
        </Cartao>
      ))}

      {alertas.dados !== null && lista.length === 0 ? (
        <Cartao>
          <Paragrafo>Nenhum alerta de calor no momento.</Paragrafo>
        </Cartao>
      ) : null}
    </ScrollView>
  );
}
