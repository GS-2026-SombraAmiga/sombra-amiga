#!/usr/bin/env bash
# Painel rápido da infraestrutura: rede, serviços, portas, últimas medições, alertas e auditoria.
# Uso: sudo bash status.sh
set -uo pipefail
[[ $EUID -eq 0 ]] || { echo "Rode com sudo: sudo bash $0" >&2; exit 1; }

LOGS=/var/log/sombra-amiga
C='\033[1;36m'; F='\033[0m'
secao() { echo; echo -e "${C}== $* ==${F}"; }

secao "Máquina"
echo "hostname: $(hostname) | $(lsb_release -ds 2>/dev/null) | ligada há $(uptime -p | sed 's/up //')"
ip -4 -br addr | grep -v '^lo' | sed 's/^/  /'
echo "  DNS: $(resolvectl dns 2>/dev/null | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | sort -u | paste -sd ' ')"

secao "Serviços"
for s in sombra-amiga-api nginx sombra-amiga-monitor auditd; do
    printf '  %-22s %-9s pid %-6s reinícios %s\n' "$s" "$(systemctl is-active "$s")" \
        "$(systemctl show -p MainPID --value "$s")" "$(systemctl show -p NRestarts --value "$s")"
done

secao "Portas em escuta"
ss -tlnp | awk 'NR>1 {split($6,p,"\""); printf "  %-22s %s\n", $4, p[2]}'

secao "Firewall"
ufw status | sed -n '1p;5,$p' | sed 's/^/  /'

secao "Saúde da API (pelo nginx)"
echo "  /api/saude: $(curl -s -m 3 http://127.0.0.1/api/saude || echo 'sem resposta')"

secao "Últimas medições ($LOGS/monitoramento.log)"
tail -n 5 "$LOGS/monitoramento.log" 2>/dev/null | sed 's/^/  /'

secao "Últimos alertas ($LOGS/alertas.log)"
tail -n 6 "$LOGS/alertas.log" 2>/dev/null | sed 's/^/  /' || echo "  nenhum"

secao "Última auditoria dos scripts ($LOGS/auditoria.log)"
tail -n 6 "$LOGS/auditoria.log" 2>/dev/null | sed 's/^/  /'
