drop table if exists log;
create table log (
  id integer primary key autoincrement,
  sujeto text not null,
  log text not null
);