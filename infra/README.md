# Infraestrutura Linux da Sombra Amiga

Parte da CitizenTech **Sombra Amiga** na disciplina **Operating Systems**.

**Integrantes:** Glauco Heitor Gonçalves (RM 555978) e Pedro Henrique Junqueira (RM 556278).

**Vídeo de demonstração:** _(link)_

Scripts Bash que preparam uma VM Ubuntu Server do zero e a deixam executando a aplicação web da Sombra Amiga: a API principal (.NET 10) e o painel de acompanhamento do calor. A VM fica monitorada, auditada e se recupera sozinha de falhas.

## Como fica a VM

```
 Windows (host)                         VM sombra-amiga (Ubuntu Server 24.04)
 ─────────────                          ──────────────────────────────────────────────
 navegador ── http://192.168.56.10 ──▶  UFW (entrada: só 22 e 80)
                                          │
                                          ▼
                                        nginx :80 ── /  ──▶ painel web (/var/www/sombra-amiga)
                                          │
                                          └──── /api, /swagger ──▶ sombra-amiga-api (127.0.0.1:5000)
                                                                     │  usuário sombra-api, sem login
                                                                     ▼
                                                                   SQLite (/var/lib/sombra-amiga)

                                        sombra-amiga-monitor ── a cada 10 s mede CPU, memória, disco,
                                                                API e nginx → /var/log/sombra-amiga
                                        auditd ── registra mudanças de configuração e kill -9
```

| Item | Valor |
|---|---|
| Sistema | Ubuntu Server 24.04.5 LTS no VirtualBox (2 GB de RAM, 1 vCPU, disco de 25 GB) |
| Placa 1 | NAT, para internet (DHCP, `enp0s3`) |
| Placa 2 | Host-only, rede interna com o Windows: **IP fixo 192.168.56.10** (`enp0s8`) |
| Hostname | `sombra-amiga` (domínio `sombra-amiga.local`) |
| DNS | 1.1.1.1 e 8.8.8.8 (systemd-resolved) |
| Fuso horário | America/Sao_Paulo |

## Arquivos

| Arquivo | O que faz |
|---|---|
| [provisionar.sh](provisionar.sh) | Roda as etapas 01, 02 e 03 em ordem, para no primeiro erro e mostra o status no final |
| [01-rede.sh](01-rede.sh) | Hostname, `/etc/hosts`, IP fixo pelo netplan, DNS, fuso horário e firewall UFW |
| [02-aplicacao.sh](02-aplicacao.sh) | Dependências (nginx, runtime ASP.NET Core 10, sqlite3), conta de serviço, configuração de ambiente, API como serviço systemd e nginx com o painel e o proxy de `/api` |
| [03-monitoramento.sh](03-monitoramento.sh) | Instala o monitor como serviço systemd tolerante a falhas, a rotação de logs e as regras de auditoria do auditd |
| [monitor.sh](monitor.sh) | O monitor em si (instalado como `/usr/local/bin/sombra-amiga-monitor`) |
| [teste-falha.sh](teste-falha.sh) | Provoca falhas de propósito e mostra a infraestrutura reagindo |
| [status.sh](status.sh) | Resumo da VM: rede, serviços, portas, firewall, saúde da API, medições, alertas e auditoria |
| [lib/comum.sh](lib/comum.sh) | Funções compartilhadas: log de auditoria, execução registrada, escrita de configuração |
| [enviar-para-vm.ps1](enviar-para-vm.ps1) | No Windows: publica a API para Linux, junta o painel e os scripts e envia tudo à VM por SSH |
| [evidencias/](evidencias) | Saídas reais do provisionamento e do teste de falha |

Todos os scripts podem ser rodados mais de uma vez. Cada configuração só é reescrita se mudou (a tela mostra `já estava atualizado`), e a API nova entra no lugar da anterior de uma vez, sem ficar pela metade.

## Como rodar

**Pré-requisitos:**
- VM Ubuntu Server 24.04 com OpenSSH, uma placa NAT e uma placa host-only (no VirtualBox, a rede host-only padrão é 192.168.56.0/24).
- Acesso SSH à VM.
- No Windows, o SDK do .NET 10, para publicar a API.

1. **Windows, na raiz do repositório:** gera o pacote e envia para a VM. Os parâmetros padrão usam o redirecionamento de porta 127.0.0.1:2222 da placa NAT; veja o topo do arquivo para trocar.

   ```
   powershell -ExecutionPolicy Bypass -File infra\enviar-para-vm.ps1
   ```

2. **Na VM:**

   ```bash
   cd ~/sombra-amiga/infra
   sudo bash provisionar.sh
   ```

   Leva cerca de 1 minuto. No final, o `status.sh` mostra tudo ativo.

3. **No navegador do Windows:** abra o painel em http://192.168.56.10/ e o Swagger em http://192.168.56.10/swagger.

4. **Opcional, para o painel mostrar um alerta:** no Windows, rode `demo\cenario-demo.ps1 -Api http://192.168.56.10/api`. Ele envia uma leitura de calor extremo e uma previsão.

## Provisionamento de rede (01-rede.sh)

1. **Hostname:** define `sombra-amiga` com `hostnamectl` e impede o cloud-init de voltar o nome antigo no boot.
2. **`/etc/hosts`:** associa o hostname a 127.0.1.1 e ao IP interno 192.168.56.10.
3. **IP fixo:** escreve `/etc/netplan/60-sombra-amiga.yaml` com 192.168.56.10/24 na placa host-only e aplica com `netplan apply`. A placa NAT continua por DHCP.
4. **DNS:** configura o systemd-resolved com 1.1.1.1 e 8.8.8.8 e testa a resolução de `github.com`.
5. **Fuso horário:** define America/Sao_Paulo, para os logs ficarem no horário de Brasília.
6. **Firewall:** o UFW nega toda entrada por padrão e libera só SSH (22) e HTTP (80). A API (5000) escuta apenas em 127.0.0.1 e não é acessível de fora.

## Provisionamento da aplicação (02-aplicacao.sh)

1. **Pacote:** confere se o pacote enviado pelo Windows está completo.
2. **Dependências:** instala `nginx`, `aspnetcore-runtime-10.0` (do repositório oficial do Ubuntu), `sqlite3`, `curl` e `python3`. A saída detalhada do apt vai para `apt.log`.
3. **Conta de serviço:** cria `sombra-api`, sem senha e sem shell de login. A API não roda como root.
4. **Configuração de ambiente:** cria `/etc/sombra-amiga/api.env` com o endereço de escuta, a string de conexão do banco e o ambiente `Production`. Só root e a conta de serviço leem esse arquivo.
5. **Publicação:** copia a API para `/opt/sombra-amiga/api` (a versão anterior fica em `api.anterior`) e o painel para `/var/www/sombra-amiga`.
6. **Serviço `sombra-amiga-api`:** é um serviço systemd com `Restart=always`, que sobe no boot e só pode escrever na pasta de dados (`ProtectSystem=strict`). Na primeira subida, a API aplica as migrations e cadastra os pontos de hidratação.
7. **nginx:** serve o painel em `/` e encaminha `/api` e `/swagger` para a API. Também ganha `Restart=always`.
8. **Verificação:** espera `/api/saude` responder `Healthy` pelo nginx. Esse health check, adicionado à API para o monitoramento, testa a conexão com o banco.

## Monitoramento como serviço (03-monitoramento.sh e monitor.sh)

O `sombra-amiga-monitor` é um serviço systemd que, a cada 10 segundos, mede:

| Medição | Como | Limite padrão |
|---|---|---|
| CPU | diferença de `/proc/stat` entre duas medições | 80% |
| Memória | `MemTotal - MemAvailable` de `/proc/meminfo` | 85% |
| Disco | `df` da partição `/` | 85% |
| API | `GET /api/saude` direto na porta 5000 | precisa responder 200 |
| nginx | `GET /` na porta 80 | precisa responder 200 |

Os limites ficam em `/etc/sombra-amiga/monitor.conf`. Depois de mudar, rode `sudo systemctl restart sombra-amiga-monitor`.

**Logs** em `/var/log/sombra-amiga/`:
- **`monitoramento.log`:** uma linha por medição, por exemplo `2026-11-14 01:38:25 CPU=100% MEMORIA=21% DISCO=13% API=ok NGINX=ok`.
- **`alertas.log`:** `[ALERTA]` quando um recurso passa do limite ou um serviço cai, e `[NORMALIZADO]` quando volta. O alerta abre uma vez e fecha uma vez, sem repetir a cada medição. Nos alertas de CPU e memória, já aparece o processo responsável.
- **journal do sistema:** os alertas também vão para lá (`journalctl -t sombra-amiga-monitor`).
- **Rotação:** o `logrotate` roda diariamente e guarda 14 dias compactados.

**Tolerância a falhas:**
- O monitor reinicia sozinho em qualquer queda, inclusive por `kill -9` (`Restart=always`), e o systemd nunca desiste de reiniciá-lo (`StartLimitIntervalSec=0`).
- Ele tem prioridade baixa de CPU (`Nice=10`), para não disputar com a aplicação.
- Ele é protegido do OOM killer (`OOMScoreAdjust=-500`): se faltar memória, o kernel mata outros processos antes.
- Uma verificação que falha não derruba o laço do monitor. O serviço da API e o nginx também usam `Restart=always`.

## Logs de auditoria e acompanhamento

Há dois níveis de auditoria:

1. **Auditoria dos scripts (`/var/log/sombra-amiga/auditoria.log`):** cada ação dos scripts gera uma linha com data, usuário real (mesmo usando sudo), script, resultado e comando. Exemplo:

   ```
   2026-11-14 01:07:00 | sombra | 02-aplicacao.sh | OK | systemctl restart sombra-amiga-api
   ```

   A saída completa de cada execução fica em `provisionamento.log` e `teste-falha.log`.

2. **Auditoria do sistema (auditd):** regras em `/etc/audit/rules.d/sombra-amiga.rules` registram quem alterou:
   - as configurações da aplicação, os serviços e o código publicado;
   - a rede (netplan, `/etc/hosts`);
   - os acessos (sudoers, `/etc/passwd`).

   Também registram todo `kill -9` enviado a qualquer processo. Para consultar:

   ```bash
   sudo aureport -k --summary            # eventos por regra
   sudo ausearch -k sombra-kill -i       # quem mandou kill -9 e em qual processo
   sudo ausearch -k sombra-config -i     # quem mexeu nas configurações
   ```

## Teste de falha (teste-falha.sh)

```bash
sudo bash teste-falha.sh          # todos os cenários (cerca de 2 minutos)
sudo bash teste-falha.sh api      # ou só um: api, monitor, cpu, memoria, disco
```

| Cenário | O que provoca | O que se espera |
|---|---|---|
| `api` | `kill -9` no processo da API | O systemd sobe um processo novo em cerca de 4 s, o nginx volta a responder `Healthy` e o auditd mostra quem matou |
| `monitor` | `kill -9` no próprio monitor | O systemd o reinicia em cerca de 5 s |
| `cpu` | CPU a 100% por 30 s | `[ALERTA] CPU` apontando o processo, e depois `[NORMALIZADO]` |
| `memoria` | Ocupa memória até o uso ficar 7 pontos acima do limite por 30 s | `[ALERTA] MEMORIA`, depois `[NORMALIZADO]`, e a API continua no ar |
| `disco` | Reserva um arquivo grande com `fallocate` até passar do limite e o apaga | `[ALERTA] DISCO`, e depois `[NORMALIZADO]` |

Resultado real da execução, em [evidencias/teste-falha.txt](evidencias/teste-falha.txt):

```
==> Falha 1: kill -9 na API
    PID novo:  6449 | reinícios agora: 1 | voltou em 4s
    ok: API respondendo de novo pelo nginx: Healthy
      auid=sombra (quem logou) uid=root comm=bash -> matou opid=4855 ocomm=dotnet
==> Falha 3: CPU a 100% por 30s (limite 80%)
    alertas.log: 2026-11-14 01:38:15 [ALERTA] CPU em 100% (limite 80%); maior consumo: yes (pid 6552, 97.8%)
    alertas.log: 2026-11-14 01:38:46 [NORMALIZADO] CPU voltou a 0% (limite 80%)
```

Também testamos reiniciar a VM: rede, firewall, API, nginx, monitor e auditd voltaram sozinhos.

## Evidências

| Arquivo | Conteúdo |
|---|---|
| [status.txt](evidencias/status.txt) | Saída do `status.sh` depois do provisionamento |
| [teste-falha.txt](evidencias/teste-falha.txt) | Execução completa do `teste-falha.sh` |
| [alertas.log](evidencias/alertas.log) | Alertas gerados durante o teste |
| [monitoramento-durante-teste.log](evidencias/monitoramento-durante-teste.log) | Medições durante o teste |
| [journal-reinicios.txt](evidencias/journal-reinicios.txt) | O systemd reiniciando a API e o monitor |
| [auditoria.log](evidencias/auditoria.log) | Auditoria dos scripts (provisionamento, reexecução e testes) |
| [auditd.txt](evidencias/auditd.txt) | Resumo do auditd e os `kill -9` registrados |

## Limitações

- A Rede de Apoio (Java e MySQL) não roda nesta VM; o envio de pedidos de ajuda fica desligado aqui (`RedeDeApoio__Url` vazio). Em produção, ela ficaria em outro servidor.
- O painel é servido por HTTP. Em produção, o nginx usaria HTTPS com certificado.
- O pacote da API é compilado no Windows e enviado por SSH. Assim a VM só precisa do runtime, e não do SDK, que é maior.
