#!/usr/bin/env bash
# Teste de falha: provoca problemas de propósito e mostra a infraestrutura reagindo.
#   api      kill -9 na API: o systemd a reinicia e a auditoria registra quem matou
#   monitor  kill -9 no próprio monitor: o systemd o reinicia
#   cpu      CPU a 100%: o monitor gera ALERTA e depois NORMALIZADO
#   memoria  ocupa a memória até passar do limite: ALERTA e NORMALIZADO
#   disco    reserva um arquivo grande até passar do limite: ALERTA e NORMALIZADO
#   tudo     todos acima, em sequência (padrão)
# Uso: sudo bash teste-falha.sh [api|monitor|cpu|memoria|disco|tudo]
DIR_INFRA=$(dirname "$(readlink -f "$0")")
LOG_SAIDA=/var/log/sombra-amiga/teste-falha.log
source "$DIR_INFRA/lib/comum.sh"

SERVICO_API=sombra-amiga-api
SERVICO_MONITOR=sombra-amiga-monitor
ALERTAS=/var/log/sombra-amiga/alertas.log
ARQUIVO_DISCO=/var/tmp/sombra-teste-disco.img
DURACAO_CARGA=30   # segundos de carga em CPU e memória
source /etc/sombra-amiga/monitor.conf

pid_de() { systemctl show -p MainPID --value "$1"; }
reinicios_de() { systemctl show -p NRestarts --value "$1"; }

# Espera aparecer no alertas.log uma linha NOVA com o padrão informado.
esperar_alerta() {
    local padrao=$1 linhas_antes=$2 limite=${3:-60}
    for ((s = 0; s < limite; s++)); do
        if tail -n +"$((linhas_antes + 1))" "$ALERTAS" | grep -q "$padrao"; then
            tail -n +"$((linhas_antes + 1))" "$ALERTAS" | grep "$padrao" | tail -1 | sed 's/^/    alertas.log: /'
            return 0
        fi
        sleep 1
    done
    echo "    (nenhuma linha \"$padrao\" em ${limite}s)"
    return 1
}

linhas_alertas() { wc -l < "$ALERTAS"; }

# Mata um serviço com kill -9 e espera o systemd subir um processo novo.
matar_e_esperar() {
    local servico=$1 pid_antigo reinicios pid_novo inicio
    pid_antigo=$(pid_de "$servico")
    reinicios=$(reinicios_de "$servico")
    echo "    PID atual: $pid_antigo | reinícios até agora: $reinicios"
    inicio=$(date +%s)
    executar kill -9 "$pid_antigo"
    for ((s = 0; s < 30; s++)); do
        pid_novo=$(pid_de "$servico")
        if [[ $pid_novo != 0 && $pid_novo != "$pid_antigo" ]] && systemctl is-active --quiet "$servico"; then
            break
        fi
        sleep 1
    done
    echo "    PID novo:  $pid_novo | reinícios agora: $(reinicios_de "$servico") | voltou em $(($(date +%s) - inicio))s"
    journalctl -u "$servico" --since "-1min" --no-pager -o short-iso | grep -E "Main process exited|Scheduled restart|Started" | tail -3 | sed 's/^/    journal: /' || true
}

teste_api() {
    titulo "Falha 1: kill -9 na API"
    matar_e_esperar "$SERVICO_API"
    if esperar_url http://127.0.0.1/api/saude 20; then
        ok "API respondendo de novo pelo nginx: $(curl -s http://127.0.0.1/api/saude)"
    fi
    echo "    Auditoria (auditd) de quem mandou o kill -9:"
    # --input-logs: lê o audit.log mesmo quando a entrada padrão não é um terminal.
    ausearch --input-logs -k sombra-kill -i --start recent 2> /dev/null < /dev/null | awk '
        /^type=OBJ_PID/ { for (i = 1; i <= NF; i++) { if ($i ~ /^opid=/) alvo = $i; if ($i ~ /^ocomm=/) nome = $i } }
        /^type=SYSCALL/ { for (i = 1; i <= NF; i++) { if ($i ~ /^auid=/) quem = $i; if ($i ~ /^uid=/) uid = $i; if ($i ~ /^comm=/) cmd = $i } }
        END { if (quem) print "      " quem " (quem logou) " uid " " cmd " -> matou " alvo " " nome }' || true
}

teste_monitor() {
    titulo "Falha 2: kill -9 no próprio monitor"
    matar_e_esperar "$SERVICO_MONITOR"
    grep "monitor iniciado" /var/log/sombra-amiga/monitoramento.log | tail -1 | sed 's/^/    monitoramento.log: /'
}

teste_cpu() {
    titulo "Falha 3: CPU a 100% por ${DURACAO_CARGA}s (limite ${LIMITE_CPU}%)"
    local antes pids=()
    antes=$(linhas_alertas)
    for ((n = 0; n < $(nproc); n++)); do
        timeout "$DURACAO_CARGA" yes > /dev/null &
        pids+=($!)
    done
    auditar OK "carga de CPU iniciada ($(nproc) processos yes por ${DURACAO_CARGA}s)"
    esperar_alerta "ALERTA\] CPU" "$antes" || true
    wait "${pids[@]}" 2> /dev/null || true
    esperar_alerta "NORMALIZADO\] CPU" "$antes" || true
}

teste_memoria() {
    local total disponivel alvo_mb antes
    total=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
    disponivel=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)
    # Quanto ocupar para o uso chegar a limite + 7 pontos.
    alvo_mb=$(((disponivel - total * (100 - LIMITE_MEMORIA - 7) / 100) / 1024))
    titulo "Falha 4: ocupando ${alvo_mb} MB de memória por ${DURACAO_CARGA}s (limite ${LIMITE_MEMORIA}%)"
    antes=$(linhas_alertas)
    python3 -c "import time; b = b'x' * ($alvo_mb * 1024 * 1024); time.sleep($DURACAO_CARGA)" &
    local pid=$!
    auditar OK "carga de memória iniciada (${alvo_mb} MB por ${DURACAO_CARGA}s)"
    esperar_alerta "ALERTA\] MEMORIA" "$antes" || true
    wait "$pid" 2> /dev/null || true
    esperar_alerta "NORMALIZADO\] MEMORIA" "$antes" || true
    systemctl is-active --quiet "$SERVICO_API" && ok "a API continuou no ar durante o teste"
}

teste_disco() {
    local tamanho_kb usado_kb alvo_kb antes
    local livre_kb
    # Mesma conta do df: usado / (usado + livre), sem o espaço reservado ao root.
    read -r usado_kb livre_kb < <(df --output=used,avail -k / | tail -1)
    tamanho_kb=$((usado_kb + livre_kb))
    alvo_kb=$((tamanho_kb * (LIMITE_DISCO + 5) / 100 - usado_kb))
    titulo "Falha 5: reservando $((alvo_kb / 1024 / 1024)) GB em disco (limite ${LIMITE_DISCO}%)"
    antes=$(linhas_alertas)
    executar fallocate -l "${alvo_kb}K" "$ARQUIVO_DISCO"
    df -h / | tail -1 | awk '{print "    disco agora: " $5 " usado"}'
    esperar_alerta "ALERTA\] DISCO" "$antes" || true
    executar rm -f "$ARQUIVO_DISCO"
    esperar_alerta "NORMALIZADO\] DISCO" "$antes" || true
}

limpar() {
    rm -f "$ARQUIVO_DISCO"
    pkill -f "^yes$" 2> /dev/null || true
}
trap limpar EXIT

inicio_script
cenario=${1:-tudo}
case $cenario in
    api) teste_api ;;
    monitor) teste_monitor ;;
    cpu) teste_cpu ;;
    memoria) teste_memoria ;;
    disco) teste_disco ;;
    tudo) teste_api; teste_monitor; teste_cpu; teste_memoria; teste_disco ;;
    *) echo "Cenário desconhecido: $cenario (use api, monitor, cpu, memoria, disco ou tudo)" >&2; exit 1 ;;
esac
fim_script
