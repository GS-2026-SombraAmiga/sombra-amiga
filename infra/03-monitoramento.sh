#!/usr/bin/env bash
# 03 - Monitoramento como serviço tolerante a falhas e auditoria do sistema.
#   - instala o monitor (monitor.sh) como serviço systemd com Restart=always
#   - rotação dos logs em /var/log/sombra-amiga
#   - auditd vigiando as configurações da Sombra Amiga e quem mata processos com kill -9
# Uso: sudo bash 03-monitoramento.sh
DIR_INFRA=$(dirname "$(readlink -f "$0")")
source "$DIR_INFRA/lib/comum.sh"

# ---- Configuração (ajuste aqui) ----
SERVICO_MONITOR=sombra-amiga-monitor
LIMITE_CPU=80
LIMITE_MEMORIA=85
LIMITE_DISCO=85
INTERVALO=10
# ------------------------------------

inicio_script

titulo "1/5 Instalando o monitor em /usr/local/bin/$SERVICO_MONITOR"
executar install -m 755 "$DIR_INFRA/monitor.sh" "/usr/local/bin/$SERVICO_MONITOR"
escrever_arquivo /etc/sombra-amiga/monitor.conf 644 <<EOF
# Gerado por infra/03-monitoramento.sh. Limites em % e intervalo em segundos.
# Depois de mudar: sudo systemctl restart $SERVICO_MONITOR
LIMITE_CPU=$LIMITE_CPU
LIMITE_MEMORIA=$LIMITE_MEMORIA
LIMITE_DISCO=$LIMITE_DISCO
INTERVALO=$INTERVALO
URL_API=http://127.0.0.1:5000/api/saude
URL_PAINEL=http://127.0.0.1/
EOF

titulo "2/5 Serviço systemd $SERVICO_MONITOR (tolerante a falhas)"
escrever_arquivo "/etc/systemd/system/$SERVICO_MONITOR.service" 644 <<EOF
# Gerado por infra/03-monitoramento.sh
[Unit]
Description=Sombra Amiga - monitoramento de CPU, memória, disco, API e nginx
After=network-online.target sombra-amiga-api.service nginx.service
Wants=network-online.target
# Nunca desiste de reiniciar, mesmo com quedas seguidas.
StartLimitIntervalSec=0

[Service]
Type=simple
ExecStart=/usr/local/bin/$SERVICO_MONITOR
# Volta sozinho em qualquer queda: erro, kill -9 ou fim inesperado.
Restart=always
RestartSec=5
# Sob falta de memória, o kernel prefere matar outros processos antes do monitor.
OOMScoreAdjust=-500
# O monitor não disputa CPU com a aplicação.
Nice=10
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ReadWritePaths=/var/log/sombra-amiga
SyslogIdentifier=$SERVICO_MONITOR

[Install]
WantedBy=multi-user.target
EOF
executar systemctl daemon-reload
executar systemctl enable "$SERVICO_MONITOR"
executar systemctl restart "$SERVICO_MONITOR"

titulo "3/5 Rotação dos logs (logrotate)"
escrever_arquivo /etc/logrotate.d/sombra-amiga 644 <<'EOF'
# Gerado por infra/03-monitoramento.sh
/var/log/sombra-amiga/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
executar logrotate --debug /etc/logrotate.d/sombra-amiga > /dev/null 2>&1

titulo "4/5 Auditoria do sistema (auditd)"
instalar_pacotes auditd
escrever_arquivo /etc/audit/rules.d/sombra-amiga.rules 640 <<'EOF'
# Gerado por infra/03-monitoramento.sh
# Consulta: sudo ausearch -k <chave> -i   (ex.: sudo ausearch -k sombra-config -i)

# Alterações nas configurações e no código da aplicação
-w /etc/sombra-amiga/ -p wa -k sombra-config
-w /etc/nginx/sites-available/sombra-amiga -p wa -k sombra-config
-w /etc/systemd/system/sombra-amiga-api.service -p wa -k sombra-servicos
-w /etc/systemd/system/sombra-amiga-monitor.service -p wa -k sombra-servicos
-w /opt/sombra-amiga/ -p wa -k sombra-aplicacao
-w /usr/local/bin/sombra-amiga-monitor -p wa -k sombra-aplicacao

# Rede e acesso administrativo
-w /etc/netplan/ -p wa -k sombra-rede
-w /etc/hosts -p wa -k sombra-rede
-w /etc/sudoers -p wa -k sombra-acesso
-w /etc/sudoers.d/ -p wa -k sombra-acesso
-w /etc/passwd -p wa -k sombra-acesso

# Quem mandou kill -9 (SIGKILL) para algum processo
-a always,exit -F arch=b64 -S kill -F a1=9 -k sombra-kill
EOF
# O auditd recusa restart manual; as regras novas entram pelo augenrules.
executar systemctl enable --now auditd
executar augenrules --load > /dev/null
auditctl -l | grep -c sombra | xargs -I{} echo "    ok: {} regras de auditoria da Sombra Amiga ativas"

titulo "5/5 Verificação"
sleep $((INTERVALO + 2))
if systemctl is-active --quiet "$SERVICO_MONITOR"; then
    ok "$SERVICO_MONITOR ativo (pid $(systemctl show -p MainPID --value "$SERVICO_MONITOR"))"
else
    echo "O monitor não está ativo:" >&2
    journalctl -u "$SERVICO_MONITOR" -n 20 --no-pager >&2
    auditar ERRO "monitor não ficou ativo"
    exit 1
fi
echo "    últimas medições (/var/log/sombra-amiga/monitoramento.log):"
tail -n 3 /var/log/sombra-amiga/monitoramento.log | sed 's/^/      /'

fim_script
