-- Coordenador inicial, para o primeiro login (o mesmo papel do admin do checkpoint).
-- Credencial de desenvolvimento documentada no README: coordenador@sombraamiga.dev / coordenador123
-- A senha esta gravada como hash BCrypt, nunca em texto puro.
insert into agentes(nome, email, senha, bairro, tipo, perfil, ativo)
values ('Coordenação Sombra Amiga', 'coordenador@sombraamiga.dev',
        '$2a$10$OOaphfm1RYURIO4w45EMLeu9zuM5pUzG72/yleMe1RIrAWSmv6jkq',
        'Brasilândia', 'AGENTE_COMUNITARIO_SAUDE', 'COORDENADOR', true);
