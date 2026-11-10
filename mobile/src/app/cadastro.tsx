import { Link, router } from 'expo-router';
import { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, Text } from 'react-native';

import { Botao, CampoTexto, Cartao, Mensagem, Paragrafo, Secao, Titulo, estilos } from '@/components/ui';
import { api, ErroApi, type Perfil } from '@/lib/api';
import { mascararCpfDigitado } from '@/lib/formato';
import { useSessao } from '@/lib/sessao';
import { cores, fontes } from '@/lib/tema';

function OpcaoPerfil(props: { titulo: string; descricao: string; selecionado: boolean; aoTocar: () => void }) {
  return (
    <Pressable
      accessibilityRole="radio"
      accessibilityState={{ selected: props.selecionado }}
      accessibilityLabel={`${props.titulo}. ${props.descricao}`}
      onPress={props.aoTocar}
      style={{
        borderWidth: props.selecionado ? 3 : 2,
        borderColor: props.selecionado ? cores.primaria : cores.borda,
        backgroundColor: props.selecionado ? '#DBEAFE' : cores.fundo,
        borderRadius: 14,
        padding: 16,
        gap: 4,
      }}>
      <Text style={{ fontSize: fontes.destaque, fontWeight: '800', color: cores.texto }}>
        {props.selecionado ? '● ' : '○ '}
        {props.titulo}
      </Text>
      <Text style={{ fontSize: fontes.pequena, color: cores.textoSuave }}>{props.descricao}</Text>
    </Pressable>
  );
}

export default function Cadastro() {
  const { entrar, urlApi } = useSessao();
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [nome, setNome] = useState('');
  const [cpf, setCpf] = useState('');
  const [contato, setContato] = useState('');
  const [condicaoSaude, setCondicaoSaude] = useState('');
  const [ocupacao, setOcupacao] = useState('');
  const [erro, setErro] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  // Conferencia simples antes de enviar; o CPF e validado pela API.
  function faltando(): string | null {
    if (!perfil) return 'Escolha se você é idoso ou trabalha na rua.';
    if (!nome.trim()) return 'Informe seu nome.';
    if (cpf.replace(/\D/g, '').length !== 11) return 'O CPF precisa ter 11 números.';
    if (!contato.trim()) return 'Informe o contato de alguém da família.';
    if (perfil === 'TrabalhadorDeRua' && !ocupacao.trim()) return 'Informe o que você faz na rua.';
    return null;
  }

  async function cadastrar() {
    const problema = faltando();
    if (problema) {
      setErro(problema);
      return;
    }
    setErro(null);
    setEnviando(true);
    try {
      const criado = await api.cadastrar(urlApi, {
        perfil: perfil!,
        nome: nome.trim(),
        cpf: cpf.replace(/\D/g, ''),
        contatoFamiliar: contato.trim(),
        condicaoSaude: condicaoSaude.trim() || undefined,
        ocupacao: perfil === 'TrabalhadorDeRua' ? ocupacao.trim() : undefined,
      });
      await entrar({ id: criado.id, nome: criado.nome, perfil: criado.perfil, temCondicaoSaude: criado.temCondicaoSaude });
      router.replace('/');
    } catch (e) {
      setErro(
        e instanceof ErroApi && e.semConexao
          ? 'Sem conexão com o servidor. Verifique a internet ou o endereço em "Configurar conexão".'
          : e instanceof Error ? e.message : 'Não foi possível cadastrar.',
      );
    } finally {
      setEnviando(false);
    }
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView contentContainerStyle={estilos.tela} keyboardShouldPersistTaps="handled">
        <Titulo>Bem-vindo ao Sombra Amiga</Titulo>
        <Paragrafo>Avisamos quando o calor fica perigoso e mostramos onde encontrar sombra e água.</Paragrafo>

        <Secao>Quem é você?</Secao>
        <OpcaoPerfil
          titulo="Sou idoso(a)"
          descricao="Tenho 60 anos ou mais"
          selecionado={perfil === 'Idoso'}
          aoTocar={() => setPerfil('Idoso')}
        />
        <OpcaoPerfil
          titulo="Trabalho na rua"
          descricao="Entregador, ambulante, gari e outros"
          selecionado={perfil === 'TrabalhadorDeRua'}
          aoTocar={() => setPerfil('TrabalhadorDeRua')}
        />

        <CampoTexto rotulo="Seu nome" value={nome} onChangeText={setNome} autoComplete="name" textContentType="name" />
        <CampoTexto
          rotulo="CPF"
          value={cpf}
          onChangeText={(t) => setCpf(mascararCpfDigitado(t))}
          keyboardType="number-pad"
          placeholder="000.000.000-00"
        />
        <CampoTexto
          rotulo="Contato de alguém da família"
          ajuda="Nome e telefone de quem deve ser avisado"
          value={contato}
          onChangeText={setContato}
        />
        {perfil === 'TrabalhadorDeRua' ? (
          <CampoTexto rotulo="O que você faz na rua?" value={ocupacao} onChangeText={setOcupacao} placeholder="Ex.: entregador" />
        ) : null}
        <CampoTexto
          rotulo="Condição de saúde (opcional)"
          ajuda="Ex.: pressão alta. Ajuda a calcular melhor o seu risco."
          value={condicaoSaude}
          onChangeText={setCondicaoSaude}
        />

        <Cartao>
          <Paragrafo suave>
            Seus dados ficam protegidos: o CPF, o contato e a condição de saúde não aparecem para outras pessoas, e o
            celular guarda só o seu nome.
          </Paragrafo>
        </Cartao>

        {erro ? <Mensagem tipo="erro" texto={erro} /> : null}
        <Botao titulo="Cadastrar" aoTocar={cadastrar} carregando={enviando} />

        <Link href="/configuracoes" asChild>
          <Pressable accessibilityRole="link" hitSlop={8}>
            <Text style={{ fontSize: fontes.normal, color: cores.primaria, fontWeight: '700', textAlign: 'center' }}>
              Configurar conexão
            </Text>
          </Pressable>
        </Link>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
