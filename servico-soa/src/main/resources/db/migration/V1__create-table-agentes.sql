create table agentes(
    id bigint not null auto_increment,
    nome varchar(100) not null,
    email varchar(100) not null unique,
    senha varchar(255) not null,
    bairro varchar(100) not null,
    tipo varchar(30) not null,
    perfil varchar(20) not null,
    ativo boolean not null,

    primary key(id)
);
