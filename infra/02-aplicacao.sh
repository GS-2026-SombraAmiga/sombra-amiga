#!/usr/bin/env bash
# 02 - Provisionamento da aplicação: dependências, conta de serviço, API como serviço systemd
#      e painel web publicado pelo nginx (que também encaminha /api para a API).
# Uso: sudo bash 02-aplicacao.sh
# Espera o pacote gerado por enviar-para-vm.ps1 em ../pacote (api/ e painel/).
DIR_INFRA=$(dirname "$(readlink -f "$0")")
source "$DIR_INFRA/lib/comum.sh"

# ---- Configuração (ajuste aqui) ----
PACOTE=${PACOTE:-$DIR_INFRA/../pacote}
USUARIO_SERVICO=sombra-api
DIR_API=/opt/sombra-amiga/api
DIR_PAINEL=/var/www/sombra-amiga
DIR_DADOS=/var/lib/sombra-amiga
DIR_CONFIG=/etc/sombra-amiga
PORTA_API=5000   # só escuta em 127.0.0.1; de fora, o acesso é pelo nginx na porta 80
SERVICO_API=sombra-amiga-api
DEPENDENCIAS=(nginx aspnetcore-runtime-10.0 sqlite3 curl python3)
# ------------------------------------

inicio_script

titulo "1/7 Conferindo o pacote da aplicação em $PACOTE"
for item in api/SombraAmiga.Api.dll painel/index.html; do
    if [[ ! -f $PACOTE/$item ]]; then
        echo "Pacote incompleto: falta $PACOTE/$item. Rode o enviar-para-vm.ps1 no Windows." >&2
        auditar ERRO "pacote incompleto: falta $item"
        exit 1
    fi
done
ok "pacote encontrado ($(du -sh "$PACOTE" | cut -f1))"

titulo "2/7 Dependências: ${DEPENDENCIAS[*]}"
instalar_pacotes "${DEPENDENCIAS[@]}"
ok "$(dotnet --list-runtimes | grep AspNetCore)"

titulo "3/7 Conta de serviço $USUARIO_SERVICO (sem login e sem senha)"
if id "$USUARIO_SERVICO" > /dev/null 2>&1; then
    ok "conta já existe"
else
    executar useradd --system --no-create-home --home-dir "$DIR_DADOS" --shell /usr/sbin/nologin "$USUARIO_SERVICO"
fi
executar install -d -m 750 -o "$USUARIO_SERVICO" -g "$USUARIO_SERVICO" "$DIR_DADOS"
executar install -d -m 755 "$DIR_CONFIG" /opt/sombra-amiga

titulo "4/7 Configuração de ambiente da API ($DIR_CONFIG/api.env)"
escrever_arquivo "$DIR_CONFIG/api.env" 640 <<EOF
# Gerado por infra/02-aplicacao.sh. Lido pelo serviço $SERVICO_API.
ASPNETCORE_ENVIRONMENT=Production
ASPNETCORE_URLS=http://127.0.0.1:$PORTA_API
ConnectionStrings__Padrao=Data Source=$DIR_DADOS/sombra-amiga.db
# A Rede de Apoio (Java) roda em outro servidor; vazio desliga o envio nesta VM.
RedeDeApoio__Url=
DOTNET_CLI_TELEMETRY_OPTOUT=1
EOF
chgrp "$USUARIO_SERVICO" "$DIR_CONFIG/api.env"

titulo "5/7 Publicando a API em $DIR_API e o painel em $DIR_PAINEL"
# Copia para uma pasta nova e troca de uma vez, para nunca ficar com versão pela metade.
executar rm -rf "$DIR_API.novo"
executar cp -a "$PACOTE/api" "$DIR_API.novo"
if [[ -d $DIR_API ]]; then
    executar rm -rf "$DIR_API.anterior"
    executar mv "$DIR_API" "$DIR_API.anterior"
fi
executar mv "$DIR_API.novo" "$DIR_API"
executar chown -R root:root "$DIR_API"
executar rm -rf "$DIR_PAINEL"
executar cp -a "$PACOTE/painel" "$DIR_PAINEL"
executar chown -R root:root "$DIR_PAINEL"

titulo "6/7 Serviço systemd $SERVICO_API (reinicia sozinho se cair)"
escrever_arquivo "/etc/systemd/system/$SERVICO_API.service" 644 <<EOF
# Gerado por infra/02-aplicacao.sh
[Unit]
Description=Sombra Amiga - API principal (.NET)
After=network-online.target
Wants=network-online.target
# Nunca desiste de reiniciar, mesmo com quedas seguidas.
StartLimitIntervalSec=0

[Service]
Type=simple
User=$USUARIO_SERVICO
Group=$USUARIO_SERVICO
WorkingDirectory=$DIR_API
EnvironmentFile=$DIR_CONFIG/api.env
ExecStart=/usr/bin/dotnet $DIR_API/SombraAmiga.Api.dll
Restart=always
RestartSec=3
# Isolamento: a API só escreve na pasta de dados.
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ReadWritePaths=$DIR_DADOS
SyslogIdentifier=$SERVICO_API

[Install]
WantedBy=multi-user.target
EOF
executar systemctl daemon-reload
executar systemctl enable "$SERVICO_API"
executar systemctl restart "$SERVICO_API"

titulo "7/7 nginx: painel em / e proxy de /api e /swagger para a API"
escrever_arquivo /etc/nginx/sites-available/sombra-amiga 644 <<EOF
# Gerado por infra/02-aplicacao.sh
server {
    listen 80 default_server;
    server_name _;

    root $DIR_PAINEL;
    index index.html;

    access_log /var/log/nginx/sombra-amiga.access.log;
    error_log  /var/log/nginx/sombra-amiga.error.log;

    location / {
        try_files \$uri \$uri/ =404;
    }

    location ~ ^/(api|swagger)(/|\$) {
        proxy_pass http://127.0.0.1:$PORTA_API;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_connect_timeout 3s;
        proxy_read_timeout 15s;
    }
}
EOF
executar ln -sf /etc/nginx/sites-available/sombra-amiga /etc/nginx/sites-enabled/sombra-amiga
executar rm -f /etc/nginx/sites-enabled/default
# O nginx também volta sozinho se o processo morrer.
escrever_arquivo /etc/systemd/system/nginx.service.d/reiniciar.conf 644 <<'EOF'
# Gerado por infra/02-aplicacao.sh
[Unit]
StartLimitIntervalSec=0

[Service]
Restart=always
RestartSec=3
EOF
executar systemctl daemon-reload
executar nginx -t
executar systemctl enable nginx
executar systemctl restart nginx

titulo "Verificação"
if esperar_url "http://127.0.0.1/api/saude" 40; then
    ok "API saudável pelo nginx: $(curl -s http://127.0.0.1/api/saude)"
else
    echo "A API não respondeu. Últimas linhas do serviço:" >&2
    journalctl -u "$SERVICO_API" -n 20 --no-pager >&2
    auditar ERRO "API não respondeu em /api/saude"
    exit 1
fi
ok "pontos de hidratação cadastrados: $(curl -s http://127.0.0.1/api/pontos | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))')"
IP_PAINEL=$(hostname -I | tr ' ' '\n' | grep -m1 '^192\.168\.56\.' || echo 127.0.0.1)
ok "painel: http://$IP_PAINEL/  (no navegador do Windows)"
ok "Swagger: http://$IP_PAINEL/swagger"

fim_script
