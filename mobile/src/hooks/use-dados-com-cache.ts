import { useFocusEffect } from 'expo-router';
import { useSQLiteContext } from 'expo-sqlite';
import { useCallback, useEffect, useState } from 'react';

import { ErroApi } from '@/lib/api';
import { lerCache, salvarCache } from '@/lib/banco';

interface Estado<T> {
  dados: T | null;
  atualizadoEm: string | null;
  /** true quando nao foi possivel falar com o servidor e os dados vem do aparelho. */
  semConexao: boolean;
  erro: string | null;
  carregando: boolean;
}

/**
 * Mostra primeiro o que esta salvo no aparelho e depois busca dados novos.
 * Sem internet, a tela continua com os ultimos dados e o horario em que foram obtidos.
 * Recarrega sempre que a tela volta a ficar visivel.
 */
export function useDadosComCache<T>(chave: string, buscar: () => Promise<T>) {
  const db = useSQLiteContext();
  const [estado, setEstado] = useState<Estado<T>>({
    dados: null, atualizadoEm: null, semConexao: false, erro: null, carregando: true,
  });

  useEffect(() => {
    lerCache<T>(db, chave).then((salvo) => {
      if (salvo) {
        setEstado((e) => (e.dados === null ? { ...e, dados: salvo.dados, atualizadoEm: salvo.atualizadoEm } : e));
      }
    });
  }, [db, chave]);

  const recarregar = useCallback(async () => {
    setEstado((e) => ({ ...e, carregando: true, erro: null }));
    try {
      const dados = await buscar();
      const atualizadoEm = await salvarCache(db, chave, dados);
      setEstado({ dados, atualizadoEm, semConexao: false, erro: null, carregando: false });
    } catch (e) {
      const erro = e instanceof ErroApi ? e : new ErroApi('Erro inesperado.');
      setEstado((anterior) => ({
        ...anterior,
        carregando: false,
        semConexao: erro.semConexao,
        erro: erro.semConexao ? null : erro.message,
      }));
    }
  }, [db, chave, buscar]);

  useFocusEffect(
    useCallback(() => {
      recarregar();
    }, [recarregar]),
  );

  return { ...estado, recarregar };
}
