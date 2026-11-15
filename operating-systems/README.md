# Global Solution 2026.2 — Operating Systems

**CitizenTech Sombra Amiga — Nó de Infraestrutura Linux**

## Identificação da equipe

- **Aluno líder:** Glauco Heitor Gonçalves
- **RM do líder:** 555978
- **Turma:** 3ESPG
- **Nome do ZIP:** `GS_OS_GlaucoGoncalves_RM555978.zip`
- **Prazo:** 19/11/2026 às 23h59, horário de Brasília.

A equipe e a CitizenTech são as mesmas nas demais disciplinas da GS.

| Nome completo | RM | Turma | Login nas duas VMs | Papel | Líder |
|---|---|---|---|---|---|
| Glauco Heitor Gonçalves | 555978 | 3ESPG | `GlaucoGoncalves_RM555978` | Administrador | Sim |
| Pedro Henrique Junqueira | 556278 | 3ESPG | `PedroJunqueira_RM556278` | Executor do agente | Não |

### Contas dos integrantes

As duas contas existem no CT-NODE e no CT-CLIENT, com o mesmo login, e pertencem ao grupo operacional `citizenops`.

- **Login do administrador:** `GlaucoGoncalves_RM555978` (membro do grupo `sudo`)
- **Login do executor do agente, usado em `User=`:** `PedroJunqueira_RM556278` (sem `sudo`)
- **RM da equipe, igual ao RM do líder e ao campo `TEAM` do agente:** `RM555978`

## CitizenTech

- **Nome da solução:** Sombra Amiga
- **Cidade e bairro ou território atendido:** São Paulo, Brasilândia (zona norte)
- **Cidadão beneficiado:** idosos e trabalhadores de rua expostos ao calor extremo
- **Problema em uma frase:** nos dias de calor extremo, idosos e trabalhadores de rua não sabem a tempo que correm risco nem onde encontrar sombra e água por perto.
- **Como a solução ajuda:** sensores nos pontos de hidratação medem o calor, um modelo prevê o risco do dia seguinte e o app avisa o cidadão, mostra os pontos de sombra e água próximos e permite um check-in "estou bem" para um familiar acompanhar.
- **Indicador proposto de impacto e como poderia ser medido:** percentual de check-ins "estou bem" confirmados em dias de alerta de calor. A medida seria o número de cidadãos cadastrados que confirmaram o check-in nos dias de alerta, dividido pelo total de cidadãos cadastrados que receberam o alerta.
- **Zona DNS:** `sombraamiga.test`

## Agenda 2030 e ODS

Consultados na página da [ONU Brasil](https://brasil.un.org/pt-br/sdgs).

| ODS | Nome | Resumo objetivo | Como a CitizenTech contribui |
|---|---|---|---|
| 3 | Saúde e Bem-Estar | Assegurar uma vida saudável e promover o bem-estar para todas e todos, em todas as idades. A meta 3.d pede reforçar o alerta precoce e a redução de riscos à saúde. | Avisa com antecedência sobre o calor extremo, que agrava problemas cardíacos e respiratórios em idosos. O check-in permite que um familiar perceba quem não respondeu. |
| 10 | Redução das Desigualdades | Reduzir a desigualdade dentro dos países e entre eles. A meta 10.2 pede a inclusão social de todos, independentemente de idade ou condição econômica. | Atende quem mais sofre com o calor e tem menos recursos para se proteger: idosos e trabalhadores de rua de um bairro periférico. |
| 11 | Cidades e Comunidades Sustentáveis | Tornar as cidades e os assentamentos humanos inclusivos, seguros, resilientes e sustentáveis. A meta 11.7 pede acesso a espaços públicos seguros e acessíveis, em especial para pessoas idosas. | Mapeia e divulga pontos públicos de sombra e água na Brasilândia, para que o cidadão saiba onde se proteger. |
| 13 | Ação Contra a Mudança Global do Clima | Tomar medidas urgentes para combater a mudança climática e seus impactos. As metas 13.1 e 13.3 pedem adaptação a riscos climáticos e alerta precoce. | Usa dados de temperatura para prever ondas de calor e alertar a população: uma medida de adaptação a um efeito local da mudança do clima. |

## Arquitetura

| Papel lógico | Hostname com RM do líder | IP privado | Função |
|---|---|---|---|
| CT-NODE | `ct-node-rm555978` | 192.168.56.10/24 | Infraestrutura: contas, armazenamento, agente, SSH e BIND9 |
| CT-CLIENT | `ct-client-rm555978` | 192.168.56.20/24 | Cliente de testes: ping, login SSH e consultas DNS |

```
        Rede privada host-only 192.168.56.0/24, sem gateway
        (cada VM acessa a internet pela própria placa NAT)

  ┌──────────────────────────────────────┐            ┌──────────────────────────────┐
  │ CT-NODE  ct-node-rm555978            │            │ CT-CLIENT  ct-client-rm555978│
  │ 192.168.56.10  Ubuntu Desktop 24.04  │  ◀── ping ─│ 192.168.56.20                │
  │                                      │  ◀── SSH ──│ Ubuntu Desktop 24.04         │
  │ • contas NomeAluno_RM + citizenops   │  ◀── dig ──│ • contas NomeAluno_RM        │
  │ • /srv/citizentech/{data,config,logs}│            │ • cliente SSH e dig          │
  │ • 2º disco (sdb1, ext4) em .../data  │            └──────────────────────────────┘
  │ • citizentech-agent (systemd)        │
  │ • OpenSSH (porta 22)                 │
  │ • BIND9, zona sombraamiga.test       │
  └──────────────────────────────────────┘
```

## Como validar

Os testes administrativos usam a conta do administrador, `GlaucoGoncalves_RM555978`. `User=` e o dono de `status.txt` correspondem ao executor, `PedroJunqueira_RM556278`.

1. Nas duas VMs: `date --iso-8601=seconds`, `hostname`, `whoami` e `hostnamectl`.
2. Nas duas VMs: `id GlaucoGoncalves_RM555978`, `id PedroJunqueira_RM556278` e `getent group citizenops`.
3. No nó: `sudo -l -U GlaucoGoncalves_RM555978`.
4. No nó: `ls -ld /srv/citizentech /srv/citizentech/*`, `lsblk -f`, `grep '/srv/citizentech/data' /etc/fstab` e `findmnt /srv/citizentech/data`.
5. No nó: `systemctl status citizentech-agent`, `systemctl is-enabled citizentech-agent` e `systemctl show -p User -p Group -p MainPID citizentech-agent`.
6. No nó: `ps -p $(systemctl show -p MainPID --value citizentech-agent) -o user:32,group:20,pid,ppid,args`.
7. No nó: `sudo cat /srv/citizentech/data/status.txt` e `sudo journalctl -u citizentech-agent -n 10 --no-pager`. Conferir estado recente, `equipe=RM555978`, `usuario=PedroJunqueira_RM556278`, `node=ct-node-rm555978` e ausência de erro de escrita.
8. No cliente: `ping -c 4 192.168.56.10` e `ssh PedroJunqueira_RM556278@192.168.56.10`. Na sessão remota: `whoami`, `hostname` e `id`; depois `exit`.
9. No nó: `sudo named-checkconf` e `sudo named-checkzone sombraamiga.test /etc/bind/db.sombraamiga.test`.
10. No cliente: `dig @192.168.56.10 node.sombraamiga.test +short`, `dig @192.168.56.10 dados.sombraamiga.test +short` e `dig @192.168.56.10 monitor.sombraamiga.test +short`.

O DNS padrão do CT-CLIENT não foi alterado: as consultas apontam explicitamente para o CT-NODE. Cada VM tem uma placa NAT para acessar os repositórios; os testes entre elas usam a placa privada.

## Arquivos da entrega

```text
GS_OS_GlaucoGoncalves_RM555978/
├── README.md
├── relatorio.pdf
├── configs/
│   ├── citizentech-agent.service
│   ├── agent.conf
│   ├── fstab-citizentech.txt
│   ├── named.conf.local
│   └── db.sombraamiga.test
├── scripts/
│   └── citizentech-agent.sh
└── evidencias/
    └── E01_01_... a E09_..._.png
```

## Categorias de evidências

| Categoria | Conteúdo |
|---|---|
| E01 | Sistema, identidade das duas VMs, hostname com RM do líder |
| E02 | Contas de todos os alunos nas duas VMs, grupo e sudo do administrador |
| E03 | Diretórios e permissões |
| E04 | Disco, partição, montagem e fstab |
| E05 | Serviço, habilitação e processo sob a conta do executor |
| E06 | Logs e estado recente com RM da equipe, usuário e host |
| E07 | Endereço, rota e conectividade |
| E08 | SSH com conta de integrante real |
| E09 | Validação da zona e três consultas DNS remotas |

## Problema encontrado ou verificação preventiva

**Problema real: a instalação falhou com duas placas de rede.**
- **Sintoma:** a primeira instalação automática das duas VMs terminou em "Algo deu errado".
- **Diagnóstico:** no terminal da sessão de instalação, o `apt` mostrava `Temporary failure resolving 'archive.ubuntu.com'`. O `ip -br a` e o `nmcli -t dev` revelaram que o instalador cria uma única conexão para todas as placas (`netplan-zz-all-en`); ela foi ativada na host-only, sem internet, e a placa NAT ficou desconectada.
- **Correção:** reinstalamos só com a placa NAT e acrescentamos a host-only depois, com a VM desligada. O IP fixo foi configurado no sistema já instalado.

**Problema real: o login gráfico do CT-NODE travava.** O `journalctl -p err` mostrou avisos do driver de vídeo `vmwgfx`. Desativar o Wayland no GDM (`WaylandEnable=false` em `/etc/gdm3/custom.conf`) resolveu.

**Verificações preventivas:**
- **Falha de gravação:** com `sudo chattr +i /srv/citizentech/data/status.txt`, o agente registrou `ERRO`, saiu com código 1 e foi reiniciado pelo systemd. Depois de `chattr -i`, voltou a gravar `status=OK` (E06_03).
- **Reinicialização do CT-NODE:** depois do reboot, `findmnt` mostrou o volume montado; o agente estava `enabled` e `active`, o `named` e o `ssh` estavam ativos e o IP privado continuava configurado.

## Checklist de envio

- [ ] Todos os integrantes, RMs, turma, logins, papéis e líder foram conferidos.
- [ ] A equipe é a mesma nas demais disciplinas; nenhum integrante participa de outro grupo.
- [ ] As contas nominais existem nas duas VMs e os papéis foram demonstrados.
- [ ] Hostnames e campo `TEAM` usam o RM do líder real.
- [ ] `User=`, processo, arquivo de estado e logs correspondem ao aluno executor.
- [ ] As evidências mostram identidade e data, sem os nomes fictícios do tutorial.
- [ ] Há três consultas DNS distintas a partir do CT-CLIENT.
- [ ] README, relatório, configurações, script e evidências estão presentes.
- [ ] O nome da pasta raiz coincide com o nome-base do ZIP.
- [ ] Todos sabem explicar a arquitetura e repetir os testes.

## Adaptações da equipe

- **Conta de instalação.** As VMs foram instaladas pela instalação automática do VirtualBox, que cria uma conta inicial (`sombra`). O instalador do Ubuntu não aceita maiúsculas no login, por isso as contas `NomeAluno_RM` foram criadas depois, com `adduser --allow-bad-names`, como no tutorial. A conta inicial não identifica integrante e não é usada nas evidências.
- **Rede pelo terminal.** O IP fixo da placa privada foi configurado com `nmcli`, sem gateway e com `ipv4.never-default`, em vez da tela de Configurações. O resultado é o mesmo que o tutorial pede: a rota padrão continua pela placa NAT.
- **Agente com os três diretórios.**
  - Lê `PROJECT`, `TEAM` e o intervalo de `/srv/citizentech/config/agent.conf`, que o executor só pode ler.
  - Grava o estado em `/srv/citizentech/data/status.txt`.
  - Acrescenta o histórico em `/srv/citizentech/logs/agent.log`.
  - A linha de estado inclui a carga do sistema e o uso do volume de dados; acima de 90% de uso, o status passa a `ALERTA_DISCO`.
  - Se qualquer das duas gravações falhar, o agente registra `ERRO` e encerra com código 1, como no tutorial.
- **Login gráfico com Xorg.** O Wayland foi desativado no GDM das duas VMs por causa do travamento descrito acima.
- **Mensagem de boas-vindas do SSH.** A conta do executor no CT-NODE tem `~/.hushlogin`, para a mensagem de boas-vindas do Ubuntu não ocupar a tela da evidência E08.
- **Registro DNS extra.** Além de `ns1`, `node`, `dados` e `monitor`, a zona tem `cliente`, que aponta para o CT-CLIENT (192.168.56.20).
