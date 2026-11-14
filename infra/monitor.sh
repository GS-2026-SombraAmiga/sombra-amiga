#!/usr/bin/env bash
# Monitor de infraestrutura da Sombra Amiga.
# Instalado pelo 03-monitoramento.sh em /usr/local/bin/sombra-amiga-monitor e executado
# pelo serviço systemd sombra-amiga-monitor (Restart=always).
#
# A cada INTERVALO segundos mede CPU, memória e disco e testa a API e o nginx.
#   monitoramento.log  uma linha por medição
#   alertas.log        ALERTA quando um recurso passa do limite ou um serviço cai,
#                      NORMALIZADO quando volta ao normal (também vai para o journal)

# Sem "set -e": uma verificação que falha nunca pode derrubar o monitor.
set -uo pipefail

# Valores padrão, sobrescritos por /etc/sombra-amiga/monitor.conf
LIMITE_CPU=80
LIMITE_MEMORIA=85
LIMITE_DISCO=85
INTERVALO=10
URL_API=http://127.0.0.1:5000/api/saude
URL_PAINEL=http://127.0.0.1/
CONFIG=${CONFIG:-/etc/sombra-amiga/monitor.conf}
# shellcheck source=/dev/null
[[ -f $CONFIG ]] && source "$CONFIG"

DIR_LOGS=/var/log/sombra-amiga
LOG=$DIR_LOGS/monitoramento.log
ALERTAS=$DIR_LOGS/alertas.log
mkdir -p "$DIR_LOGS"

declare -A EM_ALERTA=()

agora() { date '+%F %T'; }

registrar_alerta() {
    local tipo=$1 mensagem=$2 prioridade=user.warning
    [[ $tipo == NORMALIZADO ]] && prioridade=user.notice
    echo "$(agora) [$tipo] $mensagem" >> "$ALERTAS"
    logger -t sombra-amiga-monitor -p "$prioridade" "[$tipo] $mensagem"
}

# Abre o alerta só na passagem do limite e fecha quando volta, para não repetir a cada medição.
verificar_limite() {
    local nome=$1 valor=$2 limite=$3 detalhe=${4:-}
    if ((valor >= limite)); then
        if [[ -z ${EM_ALERTA[$nome]:-} ]]; then
            EM_ALERTA[$nome]=1
            registrar_alerta ALERTA "$nome em ${valor}% (limite ${limite}%)${detalhe:+; $detalhe}"
        fi
    elif [[ -n ${EM_ALERTA[$nome]:-} ]]; then
        unset "EM_ALERTA[$nome]"
        registrar_alerta NORMALIZADO "$nome voltou a ${valor}% (limite ${limite}%)"
    fi
}

verificar_servico() {
    local nome=$1 situacao=$2
    if [[ $situacao != ok ]]; then
        if [[ -z ${EM_ALERTA[$nome]:-} ]]; then
            EM_ALERTA[$nome]=1
            registrar_alerta ALERTA "$nome fora do ar ($situacao)"
        fi
    elif [[ -n ${EM_ALERTA[$nome]:-} ]]; then
        unset "EM_ALERTA[$nome]"
        registrar_alerta NORMALIZADO "$nome respondendo de novo"
    fi
}

# /proc/stat: tempo ocupado e ocioso acumulados de todas as CPUs.
ler_cpu() {
    local _ usuario nice sistema ocioso espera irq softirq roubado
    read -r _ usuario nice sistema ocioso espera irq softirq roubado _ < /proc/stat
    echo "$((usuario + nice + sistema + irq + softirq + roubado)) $((ocioso + espera))"
}

uso_memoria() {
    awk '/^MemTotal:/ {t=$2} /^MemAvailable:/ {d=$2} END {printf "%d", (t-d)*100/t}' /proc/meminfo
}

uso_disco() {
    df --output=pcent / | tail -1 | tr -dc '0-9'
}

maior_consumo() {
    # Processo que mais usa o recurso (%cpu ou %mem), para o alerta já apontar a causa.
    ps -eo pid=,comm=,"$1"= --sort=-"$1" | awk 'NR==1 {printf "maior consumo: %s (pid %s, %s%%)", $2, $1, $3}'
}

testar_url() {
    local codigo
    codigo=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "$1")
    if [[ $codigo == 200 ]]; then echo ok; else echo "HTTP $codigo"; fi
}

encerrar() {
    echo "$(agora) monitor encerrado (sinal recebido)" >> "$LOG"
    exit 0
}
trap encerrar TERM INT

echo "$(agora) monitor iniciado (pid $$; limites CPU ${LIMITE_CPU}%, memória ${LIMITE_MEMORIA}%, disco ${LIMITE_DISCO}%; a cada ${INTERVALO}s)" >> "$LOG"

read -r ocupado_antes ocioso_antes < <(ler_cpu)
sleep 1

while true; do
    read -r ocupado ocioso < <(ler_cpu)
    total=$(((ocupado - ocupado_antes) + (ocioso - ocioso_antes)))
    cpu=0
    ((total > 0)) && cpu=$(((ocupado - ocupado_antes) * 100 / total))
    ocupado_antes=$ocupado
    ocioso_antes=$ocioso

    memoria=$(uso_memoria)
    disco=$(uso_disco)
    api=$(testar_url "$URL_API")
    painel=$(testar_url "$URL_PAINEL")

    echo "$(agora) CPU=${cpu}% MEMORIA=${memoria}% DISCO=${disco}% API=${api// /_} NGINX=${painel// /_}" >> "$LOG"

    verificar_limite CPU "$cpu" "$LIMITE_CPU" "$( ((cpu >= LIMITE_CPU)) && maior_consumo %cpu)"
    verificar_limite MEMORIA "$memoria" "$LIMITE_MEMORIA" "$( ((memoria >= LIMITE_MEMORIA)) && maior_consumo %mem)"
    verificar_limite DISCO "$disco" "$LIMITE_DISCO"
    verificar_servico API "$api"
    verificar_servico NGINX "$painel"

    # "sleep & wait" deixa o trap responder na hora ao systemctl stop.
    sleep "$INTERVALO" &
    wait $!
done
