import { router } from 'expo-router';
import { useState } from 'react';
import { ScrollView } from 'react-native';

import { Botao, CampoTexto, Cartao, Mensagem, Paragrafo, Secao, estilos } from '@/components/ui';
import { api } from '@/lib/api';
import { urlApiPadrao } from '@/lib/endereco-api';
import { useSessao } from '@/lib/sessao';
import { cores } from '@/lib/tema';

export default function Configuracoes() {
  const { cidadao, urlApi, urlApiPersonalizada, definirUrlApi, sair } = useSessao();
  const [url, setUrl] = useState(urlApi);
  const [mensagem, setMensagem] = useState<{ tipo: 'sucesso' | 'erro' | 'aviso'; texto: string } | null>(null);
  const [testando, setTestando] = useState(false);
  const [confirmandoExclusao, setConfirmandoExclusao] = useState(false);

  async function testarESalvar() {
    setTestando(true);
    setMensagem(null);
    try {
      await api.testarConexao(url);
      await definirUrlApi(url === urlApiPadrao() ? null : url);
      setMensagem({ tipo: 'sucesso', texto: 'Conexão funcionando. Endereço salvo.' });
    } catch (e) {
      setMensagem({ tipo: 'erro', texto: e instanceof Error ? e.message : 'Falha ao conectar.' });
    } finally {
      setTestando(false);
    }
  }

  async function restaurarPadrao() {
    await definirUrlApi(null);
    setUrl(urlApiPadrao());
    setMensagem({ tipo: 'aviso', texto: 'Endereço padrão restaurado.' });
  }

  async function apagarDoAparelho() {
    await sair();
    router.replace('/cadastro');
  }

  async function excluirCadastro() {
    if (!cidadao) return;
    try {
      await api.excluirCadastro(urlApi, cidadao.id);
      await apagarDoAparelho();
    } catch (e) {
      setConfirmandoExclusao(false);
      setMensagem({ tipo: 'erro', texto: e instanceof Error ? e.message : 'Não foi possível excluir.' });
    }
  }

  return (
    <ScrollView contentContainerStyle={estilos.tela} keyboardShouldPersistTaps="handled">
      <Secao>Conexão com o servidor</Secao>
      <Paragrafo suave>
        Normalmente o endereço é encontrado sozinho. Só mude se o app não conseguir se conectar.
      </Paragrafo>
      <CampoTexto
        rotulo="Endereço da API"
        value={url}
        onChangeText={setUrl}
        autoCapitalize="none"
        autoCorrect={false}
        keyboardType="url"
      />
      <Botao titulo="Testar e salvar" aoTocar={testarESalvar} carregando={testando} />
      {urlApiPersonalizada ? <Botao titulo="Usar endereço padrão" variante="secundario" aoTocar={restaurarPadrao} /> : null}
      {mensagem ? <Mensagem tipo={mensagem.tipo} texto={mensagem.texto} /> : null}

      {cidadao ? (
        <>
          <Secao>Seus dados</Secao>
          <Botao
            titulo="Apagar meus dados deste celular"
            variante="secundario"
            dica="Remove seu nome e o histórico deste aparelho. Seu cadastro continua no Sombra Amiga."
            aoTocar={apagarDoAparelho}
          />
          {confirmandoExclusao ? (
            <Cartao estilo={{ borderColor: cores.perigo, borderWidth: 2 }}>
              <Paragrafo>Seu cadastro e seus avisos serão apagados do Sombra Amiga. Essa ação não pode ser desfeita.</Paragrafo>
              <Botao titulo="Sim, excluir meu cadastro" variante="perigo" aoTocar={excluirCadastro} />
              <Botao titulo="Cancelar" variante="secundario" aoTocar={() => setConfirmandoExclusao(false)} />
            </Cartao>
          ) : (
            <Botao titulo="Excluir meu cadastro" variante="perigo" aoTocar={() => setConfirmandoExclusao(true)} />
          )}
        </>
      ) : null}
    </ScrollView>
  );
}
