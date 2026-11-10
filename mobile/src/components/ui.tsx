import { type ReactNode } from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  type TextInputProps,
  View,
  type ViewStyle,
} from 'react-native';

import type { NivelRisco } from '@/lib/api';
import { dataHora, nomeNivel } from '@/lib/formato';
import { cores, coresNivel, espaco, fontes } from '@/lib/tema';

type Variante = 'primario' | 'sucesso' | 'perigo' | 'secundario';

const fundoBotao: Record<Variante, string> = {
  primario: cores.primaria,
  sucesso: cores.sucesso,
  perigo: cores.perigo,
  secundario: cores.fundo,
};

export function Botao(props: {
  titulo: string;
  aoTocar: () => void;
  variante?: Variante;
  desabilitado?: boolean;
  carregando?: boolean;
  dica?: string;
}) {
  const variante = props.variante ?? 'primario';
  const secundario = variante === 'secundario';
  const inativo = props.desabilitado || props.carregando;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={props.titulo}
      accessibilityHint={props.dica}
      accessibilityState={{ disabled: !!inativo, busy: !!props.carregando }}
      disabled={inativo}
      onPress={props.aoTocar}
      style={({ pressed }) => [
        estilos.botao,
        { backgroundColor: fundoBotao[variante], opacity: inativo ? 0.6 : pressed ? 0.85 : 1 },
        secundario && estilos.botaoSecundario,
      ]}>
      {props.carregando ? (
        <ActivityIndicator color={secundario ? cores.primaria : '#FFFFFF'} />
      ) : (
        <Text style={[estilos.textoBotao, secundario && { color: cores.primaria }]}>{props.titulo}</Text>
      )}
    </Pressable>
  );
}

export function Cartao({ children, estilo }: { children: ReactNode; estilo?: ViewStyle }) {
  return <View style={[estilos.cartao, estilo]}>{children}</View>;
}

export function Titulo({ children }: { children: ReactNode }) {
  return (
    <Text accessibilityRole="header" style={estilos.titulo}>
      {children}
    </Text>
  );
}

export function Secao({ children }: { children: ReactNode }) {
  return (
    <Text accessibilityRole="header" style={estilos.secao}>
      {children}
    </Text>
  );
}

export function Paragrafo({ children, suave }: { children: ReactNode; suave?: boolean }) {
  return <Text style={[estilos.paragrafo, suave && { color: cores.textoSuave }]}>{children}</Text>;
}

export function Mensagem({ tipo, texto }: { tipo: 'erro' | 'sucesso' | 'aviso'; texto: string }) {
  const fundo = { erro: cores.erroFundo, sucesso: cores.sucessoFundo, aviso: cores.avisoFundo }[tipo];
  const cor = { erro: cores.perigo, sucesso: cores.sucesso, aviso: cores.avisoTexto }[tipo];
  return (
    <View
      accessibilityRole={tipo === 'erro' ? 'alert' : undefined}
      accessibilityLiveRegion="polite"
      style={[estilos.mensagem, { backgroundColor: fundo, borderColor: cor }]}>
      <Text style={[estilos.textoMensagem, { color: cor }]}>{texto}</Text>
    </View>
  );
}

/** Aviso de que a tela mostra dados salvos no aparelho, por falta de conexao. */
export function AvisoSemConexao({ atualizadoEm }: { atualizadoEm: string | null }) {
  const quando = atualizadoEm ? `Mostrando os dados de ${dataHora(atualizadoEm)}.` : 'Ainda não há dados salvos.';
  return <Mensagem tipo="aviso" texto={`Sem conexão com o servidor. ${quando}`} />;
}

export function EtiquetaNivel({ nivel }: { nivel: NivelRisco }) {
  const c = coresNivel[nivel];
  return (
    <View style={[estilos.etiqueta, { backgroundColor: c.fundo }]}>
      <Text style={[estilos.textoEtiqueta, { color: c.texto }]}>Risco {nomeNivel(nivel)}</Text>
    </View>
  );
}

export function CampoTexto(props: TextInputProps & { rotulo: string; ajuda?: string }) {
  const { rotulo, ajuda, style, ...resto } = props;
  return (
    <View style={{ gap: 6 }}>
      <Text style={estilos.rotulo}>{rotulo}</Text>
      {ajuda ? <Text style={estilos.ajuda}>{ajuda}</Text> : null}
      <TextInput
        accessibilityLabel={rotulo}
        accessibilityHint={ajuda}
        placeholderTextColor={cores.textoSuave}
        style={[estilos.campo, style]}
        {...resto}
      />
    </View>
  );
}

export function Carregando({ texto = 'Carregando...' }: { texto?: string }) {
  return (
    <View style={estilos.carregando} accessibilityLabel={texto}>
      <ActivityIndicator size="large" color={cores.primaria} />
      <Text style={estilos.paragrafo}>{texto}</Text>
    </View>
  );
}

export const estilos = StyleSheet.create({
  tela: { flexGrow: 1, padding: espaco.m, gap: espaco.m, backgroundColor: cores.fundo },
  botao: {
    minHeight: 60,
    borderRadius: 14,
    paddingHorizontal: espaco.m,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  botaoSecundario: { borderWidth: 2, borderColor: cores.primaria },
  textoBotao: { color: '#FFFFFF', fontSize: fontes.destaque, fontWeight: '700', textAlign: 'center' },
  cartao: {
    backgroundColor: cores.cartao,
    borderRadius: 16,
    padding: espaco.m,
    gap: espaco.p,
    borderWidth: 1,
    borderColor: cores.borda,
  },
  titulo: { fontSize: fontes.titulo, fontWeight: '800', color: cores.texto },
  secao: { fontSize: fontes.destaque, fontWeight: '800', color: cores.texto, marginTop: espaco.p },
  paragrafo: { fontSize: fontes.normal, color: cores.texto, lineHeight: 28 },
  mensagem: { borderWidth: 2, borderRadius: 12, padding: espaco.m },
  textoMensagem: { fontSize: fontes.normal, fontWeight: '700', lineHeight: 28 },
  etiqueta: { alignSelf: 'flex-start', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 6 },
  textoEtiqueta: { fontSize: fontes.normal, fontWeight: '800', textTransform: 'uppercase' },
  rotulo: { fontSize: fontes.normal, fontWeight: '700', color: cores.texto },
  ajuda: { fontSize: fontes.pequena, color: cores.textoSuave },
  campo: {
    minHeight: 56,
    borderWidth: 2,
    borderColor: cores.borda,
    borderRadius: 12,
    paddingHorizontal: 14,
    fontSize: fontes.normal,
    color: cores.texto,
    backgroundColor: cores.fundo,
  },
  carregando: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: espaco.m, padding: espaco.g },
});
