import { useSQLiteContext } from 'expo-sqlite';
import { createContext, type ReactNode, useContext, useEffect, useState } from 'react';

import * as banco from './banco';
import { urlApiPadrao } from './endereco-api';

const CHAVE_URL = 'url_api';

interface Sessao {
  /** undefined enquanto carrega; null quando ninguem se cadastrou neste aparelho. */
  cidadao: banco.CidadaoLocal | null | undefined;
  urlApi: string;
  urlApiPersonalizada: boolean;
  entrar(c: banco.CidadaoLocal): Promise<void>;
  sair(): Promise<void>;
  definirUrlApi(url: string | null): Promise<void>;
}

const ContextoSessao = createContext<Sessao | null>(null);

export function SessaoProvider({ children }: { children: ReactNode }) {
  const db = useSQLiteContext();
  const [cidadao, setCidadao] = useState<banco.CidadaoLocal | null | undefined>(undefined);
  const [urlSalva, setUrlSalva] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setUrlSalva(await banco.lerConfig(db, CHAVE_URL));
      setCidadao(await banco.obterCidadao(db));
    })();
  }, [db]);

  const sessao: Sessao = {
    cidadao,
    urlApi: urlSalva ?? urlApiPadrao(),
    urlApiPersonalizada: urlSalva !== null,
    async entrar(c) {
      await banco.salvarCidadao(db, c);
      setCidadao(c);
    },
    async sair() {
      await banco.apagarDadosPessoais(db);
      setCidadao(null);
    },
    async definirUrlApi(url) {
      const limpa = url?.trim().replace(/\/$/, '') || null;
      await banco.salvarConfig(db, CHAVE_URL, limpa);
      setUrlSalva(limpa);
    },
  };

  return <ContextoSessao.Provider value={sessao}>{children}</ContextoSessao.Provider>;
}

export function useSessao(): Sessao {
  const sessao = useContext(ContextoSessao);
  if (!sessao) throw new Error('useSessao precisa estar dentro de SessaoProvider');
  return sessao;
}
