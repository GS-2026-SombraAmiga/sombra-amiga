import Ionicons from '@expo/vector-icons/Ionicons';
import { Link, Redirect } from 'expo-router';
import { Tabs } from 'expo-router/js-tabs';
import { Pressable, Text } from 'react-native';

import { Carregando } from '@/components/ui';
import { useSessao } from '@/lib/sessao';
import { cores, fontes } from '@/lib/tema';

function BotaoConfiguracoes() {
  return (
    <Link href="/configuracoes" asChild>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Configurações"
        hitSlop={12}
        style={{ paddingHorizontal: 16, flexDirection: 'row', alignItems: 'center', gap: 4 }}>
        <Ionicons name="settings-outline" size={26} color={cores.primaria} />
        <Text style={{ color: cores.primaria, fontSize: fontes.pequena, fontWeight: '700' }}>Ajustes</Text>
      </Pressable>
    </Link>
  );
}

export default function LayoutAbas() {
  const { cidadao } = useSessao();

  // Primeiro acesso: sem cadastro neste aparelho, vai direto para a tela de cadastro.
  if (cidadao === undefined) return <Carregando />;
  if (cidadao === null) return <Redirect href="/cadastro" />;

  return (
    <Tabs
      screenOptions={{
        headerTitleStyle: { fontSize: fontes.destaque, fontWeight: '800', color: cores.texto },
        headerRight: () => <BotaoConfiguracoes />,
        tabBarActiveTintColor: cores.primaria,
        tabBarInactiveTintColor: cores.textoSuave,
        tabBarLabelStyle: { fontSize: 15, fontWeight: '700' },
        // Altura minima para os rotulos grandes caberem; no iPhone a area segura ja aumenta a barra.
        tabBarStyle: { minHeight: 68 },
        tabBarItemStyle: { paddingVertical: 4 },
        sceneStyle: { backgroundColor: cores.fundo },
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Início',
          tabBarAccessibilityLabel: 'Início: risco de calor e check-in',
          tabBarIcon: ({ color, size }) => <Ionicons name="sunny-outline" color={String(color)} size={size + 4} />,
        }}
      />
      <Tabs.Screen
        name="pontos"
        options={{
          title: 'Sombra e água',
          tabBarAccessibilityLabel: 'Pontos de sombra e água perto de você',
          tabBarIcon: ({ color, size }) => <Ionicons name="water-outline" color={String(color)} size={size + 4} />,
        }}
      />
      <Tabs.Screen
        name="alertas"
        options={{
          title: 'Alertas',
          tabBarAccessibilityLabel: 'Alertas de calor',
          tabBarIcon: ({ color, size }) => <Ionicons name="warning-outline" color={String(color)} size={size + 4} />,
        }}
      />
    </Tabs>
  );
}
