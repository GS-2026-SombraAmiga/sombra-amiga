import { Stack } from 'expo-router';
import { SQLiteProvider } from 'expo-sqlite';
import { StatusBar } from 'expo-status-bar';
import { Suspense } from 'react';

import { Carregando } from '@/components/ui';
import { migrar } from '@/lib/banco';
import { SessaoProvider } from '@/lib/sessao';
import { cores, fontes } from '@/lib/tema';

export default function LayoutRaiz() {
  return (
    <Suspense fallback={<Carregando texto="Abrindo o Sombra Amiga..." />}>
      <SQLiteProvider databaseName="sombra-amiga.db" onInit={migrar} useSuspense>
        <SessaoProvider>
          <StatusBar style="dark" />
          <Stack
            screenOptions={{
              headerTintColor: cores.primaria,
              headerTitleStyle: { fontSize: fontes.destaque, fontWeight: '800', color: cores.texto },
              headerBackTitle: 'Voltar',
              contentStyle: { backgroundColor: cores.fundo },
            }}>
            <Stack.Screen name="(abas)" options={{ headerShown: false }} />
            <Stack.Screen name="cadastro" options={{ title: 'Cadastro', headerBackVisible: false }} />
            <Stack.Screen name="configuracoes" options={{ title: 'Configurações' }} />
          </Stack>
        </SessaoProvider>
      </SQLiteProvider>
    </Suspense>
  );
}
