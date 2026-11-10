import * as Location from 'expo-location';
import { useCallback, useState } from 'react';
import { Linking, Platform, RefreshControl, ScrollView, Switch, Text, View } from 'react-native';

import { AvisoSemConexao, Botao, Cartao, Mensagem, Paragrafo, estilos } from '@/components/ui';
import { useDadosComCache } from '@/hooks/use-dados-com-cache';
import { api, type Ponto } from '@/lib/api';
import { distancia, nomeTipoPonto } from '@/lib/formato';
import { useSessao } from '@/lib/sessao';
import { cores, fontes } from '@/lib/tema';

// Centro da area de demonstracao (Brasilandia, zona norte de Sao Paulo),
// onde ficam os pontos simulados do projeto.
const BRASILANDIA = { latitude: -23.462, longitude: -46.681 };

function abrirNoMapa(p: Ponto) {
  const destino = `${p.latitude},${p.longitude}`;
  const url =
    Platform.OS === 'ios'
      ? `https://maps.apple.com/?daddr=${destino}`
      : `https://www.google.com/maps/dir/?api=1&destination=${destino}`;
  Linking.openURL(url);
}

export default function Pontos() {
  const { urlApi } = useSessao();
  const [posicao, setPosicao] = useState(BRASILANDIA);
  const [usandoGps, setUsandoGps] = useState(false);
  const [raioKm, setRaioKm] = useState(2);
  const [avisoGps, setAvisoGps] = useState<string | null>(null);

  const pontos = useDadosComCache(
    'pontos',
    useCallback(() => api.pontosProximos(urlApi, posicao.latitude, posicao.longitude, raioKm), [urlApi, posicao, raioKm]),
  );

  async function alternarGps(ligar: boolean) {
    setAvisoGps(null);
    if (!ligar) {
      setUsandoGps(false);
      setPosicao(BRASILANDIA);
      return;
    }
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      setAvisoGps('Sem permissão de localização. Mostrando os pontos da área de demonstração.');
      return;
    }
    try {
      const atual = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      setPosicao({ latitude: atual.coords.latitude, longitude: atual.coords.longitude });
      setUsandoGps(true);
    } catch {
      setAvisoGps('Não foi possível encontrar sua localização agora.');
    }
  }

  const lista = pontos.dados ?? [];

  return (
    <ScrollView
      contentContainerStyle={estilos.tela}
      refreshControl={<RefreshControl refreshing={pontos.carregando && pontos.dados !== null} onRefresh={pontos.recarregar} />}>
      <Paragrafo>Lugares para parar na sombra e beber água, do mais perto ao mais longe.</Paragrafo>

      <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
        <Text style={[estilos.paragrafo, { flex: 1, fontWeight: '700' }]}>Usar minha localização</Text>
        <Switch
          accessibilityLabel="Usar minha localização"
          value={usandoGps}
          onValueChange={alternarGps}
          trackColor={{ true: cores.primaria, false: cores.borda }}
        />
      </View>
      <Paragrafo suave>
        {usandoGps ? 'Buscando a partir de onde você está.' : 'Buscando a partir da Brasilândia (área de demonstração).'}
      </Paragrafo>

      {avisoGps ? <Mensagem tipo="aviso" texto={avisoGps} /> : null}
      {pontos.semConexao ? <AvisoSemConexao atualizadoEm={pontos.atualizadoEm} /> : null}
      {pontos.erro ? <Mensagem tipo="erro" texto={pontos.erro} /> : null}

      {lista.map((p) => (
        <Cartao key={p.id}>
          <Text style={[estilos.secao, { marginTop: 0 }]}>{p.nome}</Text>
          <Text style={{ fontSize: fontes.normal, color: cores.texto, fontWeight: '700' }}>
            {nomeTipoPonto(p.tipo)}
            {p.distanciaKm !== null ? ` · a ${distancia(p.distanciaKm)}` : ''}
          </Text>
          <Botao titulo="Como chegar" variante="secundario" dica={`Abre o mapa até ${p.nome}`} aoTocar={() => abrirNoMapa(p)} />
        </Cartao>
      ))}

      {pontos.dados !== null && lista.length === 0 ? (
        <Cartao>
          <Paragrafo>Nenhum ponto a até {raioKm} km.</Paragrafo>
          {raioKm < 5 ? <Botao titulo="Procurar até 5 km" aoTocar={() => setRaioKm(5)} /> : null}
        </Cartao>
      ) : null}
    </ScrollView>
  );
}
