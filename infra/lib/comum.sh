#!/usr/bin/env bash
# Funções compartilhadas pelos scripts de provisionamento da Sombra Amiga.
# Uso: source "$(dirname "$0")/lib/comum.sh"

set -Eeuo pipefail

DIR_LOGS=/var/log/sombra-amiga
LOG_AUDITORIA=$DIR_LOGS/auditoria.log
# Saída completa do script (cada script pode trocar definindo LOG_SAIDA antes do source).
LOG_PROVISIONAMENTO=${LOG_SAIDA:-$DIR_LOGS/provisionamento.log}
NOME_SCRIPT=$(basename "$0")
# Quem rodou o script de fato (o sudo troca o usuário para root).
QUEM=${SUDO_USER:-$(id -un)}

COR_TITULO='\033[1;36m'
COR_OK='\033[1;32m'
COR_ERRO='\033[1;31m'
COR_FIM='\033[0m'

exigir_root() {
    if [[ $EUID -ne 0 ]]; then
        echo "Rode com sudo: sudo bash $0" >&2
        exit 1
    fi
}

preparar_logs() {
    mkdir -p "$DIR_LOGS"
    chmod 750 "$DIR_LOGS"
    touch "$LOG_AUDITORIA" "$LOG_PROVISIONAMENTO"
    chmod 640 "$LOG_AUDITORIA" "$LOG_PROVISIONAMENTO"
    # Toda a saída do script também vai para o log de provisionamento.
    exec > >(tee -a "$LOG_PROVISIONAMENTO") 2>&1
    trap 'falhou $LINENO "$BASH_COMMAND"' ERR
}

# Registro de auditoria: data | usuário | script | resultado | ação
auditar() {
    local resultado=$1
    shift
    printf '%s | %s | %s | %s | %s\n' "$(date '+%F %T')" "$QUEM" "$NOME_SCRIPT" "$resultado" "$*" >> "$LOG_AUDITORIA"
}

titulo() {
    echo
    echo -e "${COR_TITULO}==> $*${COR_FIM}"
}

ok() {
    echo -e "${COR_OK}    ok:${COR_FIM} $*"
}

# Executa um comando, mostra na tela e registra na auditoria com o resultado.
executar() {
    echo "    \$ $*"
    if "$@"; then
        auditar OK "$*"
    else
        local codigo=$?
        auditar "ERRO($codigo)" "$*"
        return "$codigo"
    fi
}

falhou() {
    echo -e "${COR_ERRO}ERRO na linha $1: $2${COR_FIM}" >&2
    auditar ERRO "linha $1: $2"
}

inicio_script() {
    exigir_root
    preparar_logs
    auditar INICIO "$NOME_SCRIPT iniciado em $(hostname)"
    echo -e "${COR_TITULO}### $NOME_SCRIPT ($(date '+%F %T'), usuário $QUEM)${COR_FIM}"
}

fim_script() {
    auditar FIM "$NOME_SCRIPT concluído"
    echo
    echo -e "${COR_OK}### $NOME_SCRIPT concluído${COR_FIM}"
}

# Escreve um arquivo de configuração só se o conteúdo mudou e registra na auditoria.
# Uso: escrever_arquivo /caminho permissao <<'EOF' ... EOF
escrever_arquivo() {
    local destino=$1 permissao=$2 novo
    novo=$(mktemp)
    cat > "$novo"
    if [[ -f $destino ]] && cmp -s "$novo" "$destino"; then
        rm -f "$novo"
        ok "$destino já estava atualizado"
        return
    fi
    install -D -m "$permissao" "$novo" "$destino"
    rm -f "$novo"
    auditar OK "arquivo escrito: $destino"
    ok "$destino escrito"
}

# Instala pacotes do apt. A saída detalhada do apt vai só para apt.log, para a tela ficar legível.
instalar_pacotes() {
    export DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a
    echo "    \$ apt-get install $*  (detalhes em $DIR_LOGS/apt.log)"
    if apt-get update -q >> "$DIR_LOGS/apt.log" 2>&1 \
        && apt-get install -y -q "$@" >> "$DIR_LOGS/apt.log" 2>&1; then
        auditar OK "apt-get install $*"
        for pacote in "$@"; do
            ok "$pacote $(dpkg-query -W -f='${Version}' "$pacote")"
        done
    else
        auditar ERRO "apt-get install $*"
        tail -n 20 "$DIR_LOGS/apt.log" >&2
        return 1
    fi
}

# Espera uma URL responder 200, com limite de tentativas.
esperar_url() {
    local url=$1 tentativas=${2:-30}
    for ((i = 1; i <= tentativas; i++)); do
        if curl -fs -m 3 -o /dev/null "$url"; then
            return 0
        fi
        sleep 1
    done
    return 1
}
