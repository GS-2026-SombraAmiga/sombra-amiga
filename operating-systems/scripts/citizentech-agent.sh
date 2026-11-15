#!/usr/bin/env bash
# Agente da CitizenTech Sombra Amiga no CT-NODE.
# Executado pelo systemd (citizentech-agent.service) com a conta do aluno executor e o grupo citizenops.
#
# A cada INTERVALO segundos:
#   - grava o estado atual em /srv/citizentech/data/status.txt (volume do 2o disco)
#   - acrescenta a mesma linha ao histórico em /srv/citizentech/logs/agent.log
#   - escreve a linha na saída padrão, que o journald registra
# Se qualquer gravação falhar, registra ERRO na saída de erro e encerra com código 1;
# o systemd reinicia o agente (Restart=always).

set -u
umask 007

# Valores padrão; o arquivo de configuração (só leitura para o grupo) pode sobrescrever.
PROJECT="Sombra Amiga"
TEAM="RM555978"
INTERVALO=30
LIMITE_DISCO=90
CONFIG=/srv/citizentech/config/agent.conf
if [ -r "$CONFIG" ]; then
    # shellcheck source=/dev/null
    . "$CONFIG"
fi

STATUS_FILE=/srv/citizentech/data/status.txt
LOG_FILE=/srv/citizentech/logs/agent.log

gravar() {
    # $1 = linha, $2 = arquivo, $3 = modo (> ou >>)
    if [ "$3" = ">>" ]; then
        printf '%s\n' "$1" >> "$2"
    else
        printf '%s\n' "$1" > "$2"
    fi
}

while true; do
    CARGA=$(cut -d' ' -f1 /proc/loadavg)
    USO_DADOS=$(df --output=pcent /srv/citizentech/data | tail -1 | tr -dc '0-9')
    SITUACAO=OK
    if [ "${USO_DADOS:-0}" -ge "$LIMITE_DISCO" ]; then
        SITUACAO=ALERTA_DISCO
    fi

    STATUS="$(date --iso-8601=seconds) | project=${PROJECT} | equipe=${TEAM}"
    STATUS+=" | usuario=$(id -un) | node=$(hostname)"
    STATUS+=" | carga=${CARGA} | uso_dados=${USO_DADOS}% | status=${SITUACAO}"

    if ! gravar "$STATUS" "$STATUS_FILE" ">" 2> /dev/null; then
        printf 'ERRO: nao foi possivel gravar %s\n' "$STATUS_FILE" >&2
        exit 1
    fi
    if ! gravar "$STATUS" "$LOG_FILE" ">>" 2> /dev/null; then
        printf 'ERRO: nao foi possivel gravar %s\n' "$LOG_FILE" >&2
        exit 1
    fi

    # Só chega aqui depois das duas gravações bem-sucedidas.
    printf '%s\n' "$STATUS"
    sleep "$INTERVALO"
done
