import type { SQLiteDatabase } from 'expo-sqlite';

import type { Perfil, StatusCheckIn } from './api';

// Banco SQLite no proprio aparelho. Guarda o minimo necessario: o CPF, o contato
// e a condicao de saude ficam so no servidor, nunca no celular.

const VERSAO_ATUAL = 1;

export async function migrar(db: SQLiteDatabase): Promise<void> {
  const linha = await db.getFirstAsync<{ user_version: number }>('PRAGMA user_version');
  const versao = linha?.user_version ?? 0;
  if (versao >= VERSAO_ATUAL) return;

  await db.execAsync(`
    CREATE TABLE IF NOT EXISTS cidadao (
      id TEXT PRIMARY KEY NOT NULL,
      nome TEXT NOT NULL,
      perfil TEXT NOT NULL,
      tem_condicao_saude INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS cache (
      chave TEXT PRIMARY KEY NOT NULL,
      json TEXT NOT NULL,
      atualizado_em TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS checkins (
      id TEXT PRIMARY KEY NOT NULL,
      status TEXT NOT NULL,
      data_hora_utc TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS config (
      chave TEXT PRIMARY KEY NOT NULL,
      valor TEXT NOT NULL
    );
    PRAGMA user_version = ${VERSAO_ATUAL};
  `);
}

export interface CidadaoLocal {
  id: string;
  nome: string;
  perfil: Perfil;
  temCondicaoSaude: boolean;
}

export async function obterCidadao(db: SQLiteDatabase): Promise<CidadaoLocal | null> {
  const linha = await db.getFirstAsync<{ id: string; nome: string; perfil: Perfil; tem_condicao_saude: number }>(
    'SELECT id, nome, perfil, tem_condicao_saude FROM cidadao LIMIT 1',
  );
  if (!linha) return null;
  return { id: linha.id, nome: linha.nome, perfil: linha.perfil, temCondicaoSaude: linha.tem_condicao_saude === 1 };
}

export async function salvarCidadao(db: SQLiteDatabase, c: CidadaoLocal): Promise<void> {
  await db.withTransactionAsync(async () => {
    await db.runAsync('DELETE FROM cidadao');
    await db.runAsync(
      'INSERT INTO cidadao (id, nome, perfil, tem_condicao_saude) VALUES (?, ?, ?, ?)',
      c.id, c.nome, c.perfil, c.temCondicaoSaude ? 1 : 0,
    );
  });
}

// Apaga os dados pessoais do aparelho; a configuracao de conexao e mantida.
export async function apagarDadosPessoais(db: SQLiteDatabase): Promise<void> {
  await db.execAsync('DELETE FROM cidadao; DELETE FROM cache; DELETE FROM checkins;');
}

export interface ItemCache<T> {
  dados: T;
  atualizadoEm: string;
}

export async function lerCache<T>(db: SQLiteDatabase, chave: string): Promise<ItemCache<T> | null> {
  const linha = await db.getFirstAsync<{ json: string; atualizado_em: string }>(
    'SELECT json, atualizado_em FROM cache WHERE chave = ?', chave,
  );
  return linha ? { dados: JSON.parse(linha.json) as T, atualizadoEm: linha.atualizado_em } : null;
}

export async function salvarCache<T>(db: SQLiteDatabase, chave: string, dados: T): Promise<string> {
  const agora = new Date().toISOString();
  await db.runAsync(
    'INSERT OR REPLACE INTO cache (chave, json, atualizado_em) VALUES (?, ?, ?)',
    chave, JSON.stringify(dados), agora,
  );
  return agora;
}

export interface CheckInLocal {
  id: string;
  status: StatusCheckIn;
  dataHoraUtc: string;
}

export async function registrarCheckIn(db: SQLiteDatabase, c: CheckInLocal): Promise<void> {
  await db.runAsync(
    'INSERT OR REPLACE INTO checkins (id, status, data_hora_utc) VALUES (?, ?, ?)',
    c.id, c.status, c.dataHoraUtc,
  );
}

export async function listarCheckIns(db: SQLiteDatabase, limite = 5): Promise<CheckInLocal[]> {
  const linhas = await db.getAllAsync<{ id: string; status: StatusCheckIn; data_hora_utc: string }>(
    'SELECT id, status, data_hora_utc FROM checkins ORDER BY data_hora_utc DESC LIMIT ?', limite,
  );
  return linhas.map((l) => ({ id: l.id, status: l.status, dataHoraUtc: l.data_hora_utc }));
}

export async function lerConfig(db: SQLiteDatabase, chave: string): Promise<string | null> {
  const linha = await db.getFirstAsync<{ valor: string }>('SELECT valor FROM config WHERE chave = ?', chave);
  return linha?.valor ?? null;
}

export async function salvarConfig(db: SQLiteDatabase, chave: string, valor: string | null): Promise<void> {
  if (valor === null) {
    await db.runAsync('DELETE FROM config WHERE chave = ?', chave);
  } else {
    await db.runAsync('INSERT OR REPLACE INTO config (chave, valor) VALUES (?, ?)', chave, valor);
  }
}
