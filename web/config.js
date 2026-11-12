// Configuracao do painel.
// apiUrl vazio: a API e servida no mesmo endereco do painel (nginx na VM encaminha /api).
// Para testar fora da VM, abra o painel com ?api=http://127.0.0.1:5080 no endereco.
window.SOMBRA_AMIGA_CONFIG = {
  apiUrl: '',
  intervaloSegundos: 30,
};
