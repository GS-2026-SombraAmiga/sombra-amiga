import Constants from 'expo-constants';
import { Platform } from 'react-native';

const PORTA_API = 5080;

/**
 * Endereco padrao da API principal, descoberto automaticamente:
 * - na web, o mesmo computador que serve o app;
 * - no Expo Go, o computador que roda o servidor de desenvolvimento, pelo IP da rede.
 * Pode ser trocado na tela de Configuracoes.
 */
export function urlApiPadrao(): string {
  if (Platform.OS === 'web' && typeof window !== 'undefined') {
    return `http://${window.location.hostname}:${PORTA_API}`;
  }
  const host = Constants.expoConfig?.hostUri?.split(':')[0];
  return host ? `http://${host}:${PORTA_API}` : `http://localhost:${PORTA_API}`;
}
