CREATE TABLE game (
  id SERIAL PRIMARY KEY NOT NULL,
  buy_in NUMERIC NOT NULL,
  end_time TIMESTAMP DEFAULT NULL,
  name varchar(255) DEFAULT NULL,
  rent NUMERIC NOT NULL,
  reserve NUMERIC NOT NULL,
  settled NUMERIC NOT NULL,
  start_time TIMESTAMP DEFAULT NULL
);

CREATE TABLE player (
  id SERIAL PRIMARY KEY NOT NULL,
  name varchar(255) unique DEFAULT NULL
);

CREATE TABLE buy (
  id SERIAL PRIMARY KEY NOT NULL,
  game_id bigint DEFAULT NULL,
  player_id bigint DEFAULT NULL,
  FOREIGN KEY (game_id)
      REFERENCES game (id),
  FOREIGN KEY (player_id)
      REFERENCES player (id)
);

CREATE TABLE winner (
  id SERIAL PRIMARY KEY NOT NULL,
  profit NUMERIC NOT NULL,
  share NUMERIC NOT NULL,
  value NUMERIC NOT NULL,
  game_id bigint DEFAULT NULL,
  player_id bigint DEFAULT NULL,
  FOREIGN KEY (game_id)
      REFERENCES game (id),
  FOREIGN KEY (player_id)
      REFERENCES player (id)
);

CREATE TABLE ledger (
  id SERIAL PRIMARY KEY NOT NULL,
  amount NUMERIC NOT NULL,
  ledger_time TIMESTAMP DEFAULT NULL,
  game_id bigint DEFAULT NULL,
  player_id bigint DEFAULT NULL,
  FOREIGN KEY (game_id)
      REFERENCES game (id),
  FOREIGN KEY (player_id)
      REFERENCES player (id)
);

CREATE TABLE expenses (
  id SERIAL PRIMARY KEY NOT NULL,
  amount NUMERIC NOT NULL,
  expense_time TIMESTAMP DEFAULT NULL,
  description text DEFAULT NULL
);


create view first_place as 
select distinct on (game_id) player_id,game_id,value from winner order by game_id,value desc;

create view second_place as 
select distinct on (game_id) player_id,game_id,value from winner order by game_id,value asc;

create view player_count as 
select player_id,game_id,count(*) as buyins from buy group by player_id,game_id order by game_id desc;


create view player_wins as
select c.player_id,c.game_id,c.buyins,f.player_id as first,s.player_id as second from player_count as c full join first_place as f on
(c.player_id = f.player_id ) and c.game_id = f.game_id full join second_place as s on 
(c.player_id = s.player_id ) and c.game_id = s.game_id  order by game_id desc;
