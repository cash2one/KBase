drop table if exists keyword;
create table keyword(
    id varchar(10) primary key,
    keyword varchar(20),
    importance int,
    type varchar(10)
    );

drop table if exists knowledge;
create table knowledge(
    id       varchar(10) primary key,
    qa_md5   varchar(40),
    question text,
    answer   text,
    link     text
    );

drop table if exists extend;
create table extend(
    id varchar(10) primary key,
    keyword varchar(20),
    importance int,
    type varchar(10)
    );