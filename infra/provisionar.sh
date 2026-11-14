#!/usr/bin/env bash
# Provisiona a VM inteira, na ordem: rede, aplicação, monitoramento e auditoria.
# Para no primeiro erro. Pode ser rodado de novo: cada etapa só muda o que for preciso.
# Uso: sudo bash provisionar.sh
set -Eeuo pipefail
DIR_INFRA=$(dirname "$(readlink -f "$0")")
[[ $EUID -eq 0 ]] || { echo "Rode com sudo: sudo bash $0" >&2; exit 1; }

inicio=$(date +%s)
for etapa in 01-rede.sh 02-aplicacao.sh 03-monitoramento.sh; do
    bash "$DIR_INFRA/$etapa"
done

echo
echo "Provisionamento completo em $(($(date +%s) - inicio))s."
bash "$DIR_INFRA/status.sh"
