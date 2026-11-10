create table pedidos_ajuda(
    id bigint not null auto_increment,
    cidadao_id varchar(36) not null,
    nome_cidadao varchar(120) not null,
    perfil_cidadao varchar(30) not null,
    latitude double,
    longitude double,
    status varchar(20) not null,
    agente_id bigint,
    aberto_em datetime not null,
    aceito_em datetime,
    concluido_em datetime,
    observacao varchar(500),
    versao bigint not null default 0,

    primary key(id),
    constraint fk_pedidos_ajuda_agente foreign key(agente_id) references agentes(id)
);

create index idx_pedidos_ajuda_status on pedidos_ajuda(status);
create index idx_pedidos_ajuda_cidadao on pedidos_ajuda(cidadao_id);
