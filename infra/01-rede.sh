#!/usr/bin/env bash
# 01 - Provisionamento de rede: hostname, IP fixo, /etc/hosts, DNS, fuso horário e firewall.
# Uso: sudo bash 01-rede.sh
source "$(dirname "$(readlink -f "$0")")/lib/comum.sh"

# ---- Configuração (ajuste aqui) ----
NOME_HOST=sombra-amiga
DOMINIO=sombra-amiga.local
INTERFACE_INTERNA=${INTERFACE_INTERNA:-enp0s8}   # placa host-only do VirtualBox
IP_INTERNO=192.168.56.10
PREFIXO=24
DNS_PRIMARIO=1.1.1.1
DNS_SECUNDARIO=8.8.8.8
FUSO=America/Sao_Paulo
# ------------------------------------

inicio_script

titulo "1/6 Hostname"
if [[ $(hostnamectl --static) != "$NOME_HOST" ]]; then
    executar hostnamectl set-hostname "$NOME_HOST"
else
    ok "hostname já é $NOME_HOST"
fi
# Impede o cloud-init de devolver o hostname antigo no próximo boot.
escrever_arquivo /etc/cloud/cloud.cfg.d/99-sombra-amiga.cfg 644 <<'EOF'
# Gerado por infra/01-rede.sh: o hostname e a rede são definidos pelos scripts da Sombra Amiga.
preserve_hostname: true
network: {config: disabled}
EOF

titulo "2/6 /etc/hosts"
escrever_arquivo /etc/hosts 644 <<EOF
# Gerado por infra/01-rede.sh
127.0.0.1       localhost
127.0.1.1       $NOME_HOST
$IP_INTERNO   $NOME_HOST.$DOMINIO $NOME_HOST

::1     ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF

titulo "3/6 IP fixo $IP_INTERNO/$PREFIXO na placa $INTERFACE_INTERNA (netplan)"
if ! ip link show "$INTERFACE_INTERNA" > /dev/null 2>&1; then
    echo "A placa $INTERFACE_INTERNA não existe. Placas encontradas:" >&2
    ip -br link >&2
    auditar ERRO "placa $INTERFACE_INTERNA não encontrada"
    exit 1
fi
escrever_arquivo /etc/netplan/60-sombra-amiga.yaml 600 <<EOF
# Gerado por infra/01-rede.sh: rede interna (host-only) com IP fixo.
# A placa NAT (internet) continua no 50-cloud-init.yaml, por DHCP.
network:
  version: 2
  ethernets:
    $INTERFACE_INTERNA:
      dhcp4: false
      addresses:
        - $IP_INTERNO/$PREFIXO
EOF
executar netplan apply
ok "$(ip -br addr show "$INTERFACE_INTERNA")"

titulo "4/6 DNS ($DNS_PRIMARIO e $DNS_SECUNDARIO)"
escrever_arquivo /etc/systemd/resolved.conf.d/sombra-amiga.conf 644 <<EOF
# Gerado por infra/01-rede.sh
[Resolve]
DNS=$DNS_PRIMARIO $DNS_SECUNDARIO
FallbackDNS=9.9.9.9
Domains=$DOMINIO
EOF
executar systemctl restart systemd-resolved
if resolvectl query github.com > /dev/null 2>&1; then
    ok "resolução de nomes funcionando (github.com)"
else
    echo "    aviso: não foi possível resolver github.com; confira a placa NAT" >&2
    auditar AVISO "DNS não resolveu github.com"
fi

titulo "5/6 Fuso horário $FUSO"
executar timedatectl set-timezone "$FUSO"
ok "$(date)"

titulo "6/6 Firewall (UFW): nega entrada por padrão, libera SSH e HTTP"
executar ufw default deny incoming
executar ufw default allow outgoing
executar ufw allow OpenSSH
executar ufw allow 80/tcp comment 'Painel e API da Sombra Amiga (nginx)'
executar ufw --force enable
ufw status verbose | sed 's/^/    /'

fim_script
