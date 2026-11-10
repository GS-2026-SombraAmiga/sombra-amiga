import { useSQLiteContext } from 'expo-sqlite';
import { useCallback, useEffect, useState } from 'react';
import { RefreshControl, ScrollView, Text, View } from 'react-native';

import {
  AvisoSemConexao,
  Botao,
  Cartao,
  EtiquetaNivel,
  Mensagem,
  Paragrafo,
  Secao,
  Titulo,
  estilos,
} from '@/components/ui';
import { useDadosComCache } from '@/hooks/use-dados-com-cache';
import { api, ErroApi, type RiscoAtual, type StatusCheckIn } from '@/lib/api';
import { type CheckInLocal, listarCheckIns, registrarCheckIn } from '@/lib/banco';
import { dataHora, hora, primeiroNome, temperatura } from '@/lib/formato';
import { useSessao } from '@/lib/sessao';
import { cores, coresNivel, fontes } from '@/lib/tema';

function CartaoRisco({ risco, atualizadoEm }: { risco: RiscoAtual; atualizadoEm: string | null }) {
  if (risco.nivel === null || risco.indiceCalorC === null) {
    return (
      <Cartao>
        <Text style={estilos.secao}>Calor agora</Text>
        <Paragrafo>{risco.orientacao}</Paragrafo>
      </Cartao>
    );
  }
  const c = coresNivel[risco.nivel];
  return (
    <View
      accessible
      accessibilityLabel={`Risco ${risco.nivel}. Sensação térmica de ${temperatura(risco.indiceCalorC)}. ${risco.orientacao}`}
      style={{ backgroundColor: c.fundo, borderRadius: 18, padding: 20, gap: 10 }}>
      <Text style={{ color: c.texto, fontSize: fontes.normal, fontWeight: '700' }}>Calor agora</Text>
      <Text style={{ color: c.texto, fontSize: fontes.enorme, fontWeight: '900' }}>
        {{ Baixo: 'RISCO BAIXO', Atencao: 'ATENÇÃO', Alto: 'RISCO ALTO', Extremo: 'RISCO EXTREMO' }[risco.nivel]}
      </Text>
      <Text style={{ color: c.texto, fontSize: fontes.destaque, fontWeight: '700' }}>
        Sensação de {temperatura(risco.indiceCalorC)}
      </Text>
      <Text style={{ color: c.texto, fontSize: fontes.destaque, lineHeight: 32 }}>{risco.orientacao}</Text>
      {atualizadoEm ? (
        <Text style={{ color: c.texto, fontSize: fontes.pequena }}>Atualizado às {hora(atualizadoEm)}</Text>
      ) : null}
    </View>
  );
}

export default function Inicio() {
  const db = useSQLiteContext();
  const { cidadao, urlApi } = useSessao();
  const [historico, setHistorico] = useState<CheckInLocal[]>([]);
  const [enviando, setEnviando] = useState<StatusCheckIn | null>(null);
  const [confirmandoAjuda, setConfirmandoAjuda] = useState(false);
  const [resultado, setResultado] = useState<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);

  const id = cidadao?.id ?? '';
  const risco = useDadosComCache(`risco:${id}`, useCallback(() => api.risco(urlApi, id), [urlApi, id]));
  const alertas = useDadosComCache('alertas', useCallback(() => api.alertasAtivos(urlApi), [urlApi]));
  const previsao = alertas.dados?.find((a) => a.origem === 'Previsao');

  const carregarHistorico = useCallback(() => listarCheckIns(db, 3).then(setHistorico), [db]);
  useEffect(() => {
    carregarHistorico();
  }, [carregarHistorico]);

  async function fazerCheckIn(status: StatusCheckIn) {
    setConfirmandoAjuda(false);
    setResultado(null);
    setEnviando(status);
    try {
      const checkIn = await api.checkIn(urlApi, id, status);
      await registrarCheckIn(db, { id: checkIn.id, status, dataHoraUtc: checkIn.dataHoraUtc });
      await carregarHistorico();
      setResultado({
        tipo: 'sucesso',
        texto:
          status === 'EstouBem'
            ? `Pronto! Avisamos que você está bem às ${hora(checkIn.dataHoraUtc)}.`
            : `Pedido de ajuda enviado às ${hora(checkIn.dataHoraUtc)}. A Rede de Apoio do seu bairro foi avisada.`,
      });
    } catch (e) {
      const semConexao = e instanceof ErroApi && e.semConexao;
      setResultado({
        tipo: 'erro',
        texto: semConexao
          ? 'Sem conexão: o aviso não foi enviado. Verifique a internet e tente de novo.'
          : e instanceof Error ? e.message : 'Não foi possível enviar o aviso.',
      });
    } finally {
      setEnviando(null);
    }
  }

  function atualizarTudo() {
    risco.recarregar();
    alertas.recarregar();
  }

  return (
    <ScrollView
      contentContainerStyle={estilos.tela}
      refreshControl={<RefreshControl refreshing={risco.carregando && risco.dados !== null} onRefresh={atualizarTudo} />}>
      <Titulo>Olá, {primeiroNome(cidadao?.nome ?? '')}</Titulo>

      {risco.semConexao ? <AvisoSemConexao atualizadoEm={risco.atualizadoEm} /> : null}
      {risco.erro ? <Mensagem tipo="erro" texto={risco.erro} /> : null}

      {previsao ? (
        <Cartao estilo={{ backgroundColor: cores.avisoFundo, borderColor: cores.avisoTexto, borderWidth: 2 }}>
          <EtiquetaNivel nivel={previsao.nivel} />
          <Text style={[estilos.secao, { marginTop: 0, color: cores.avisoTexto }]}>Previsão para amanhã</Text>
          <Paragrafo>{previsao.mensagem}</Paragrafo>
        </Cartao>
      ) : null}

      {risco.dados ? (
        <CartaoRisco risco={risco.dados} atualizadoEm={risco.atualizadoEm} />
      ) : (
        <Cartao>
          <Paragrafo>{risco.carregando ? 'Buscando o risco de calor...' : 'Ainda não há dados de calor.'}</Paragrafo>
        </Cartao>
      )}

      <Secao>Como você está?</Secao>
      <Botao
        titulo="Estou bem"
        variante="sucesso"
        dica="Avisa sua família de que você está bem"
        carregando={enviando === 'EstouBem'}
        desabilitado={enviando !== null}
        aoTocar={() => fazerCheckIn('EstouBem')}
      />

      {confirmandoAjuda ? (
        <Cartao estilo={{ borderColor: cores.perigo, borderWidth: 2 }}>
          <Paragrafo>Vamos avisar a Rede de Apoio do seu bairro para alguém vir ajudar. Confirma?</Paragrafo>
          <Botao titulo="Sim, preciso de ajuda" variante="perigo" aoTocar={() => fazerCheckIn('PrecisoDeAjuda')} />
          <Botao titulo="Cancelar" variante="secundario" aoTocar={() => setConfirmandoAjuda(false)} />
        </Cartao>
      ) : (
        <Botao
          titulo="Preciso de ajuda"
          variante="perigo"
          dica="Pede ajuda para a Rede de Apoio do bairro"
          carregando={enviando === 'PrecisoDeAjuda'}
          desabilitado={enviando !== null}
          aoTocar={() => setConfirmandoAjuda(true)}
        />
      )}

      {resultado ? <Mensagem tipo={resultado.tipo} texto={resultado.texto} /> : null}

      {historico.length > 0 ? (
        <>
          <Secao>Seus últimos avisos</Secao>
          {historico.map((c) => (
            <Paragrafo key={c.id} suave>
              {c.status === 'EstouBem' ? 'Estou bem' : 'Pedido de ajuda'}: {dataHora(c.dataHoraUtc)}
            </Paragrafo>
          ))}
        </>
      ) : null}
    </ScrollView>
  );
}
