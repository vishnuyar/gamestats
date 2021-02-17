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

CREATE VIEW 'playerbuyins' as select game_id,player_id,COUNT(player_id) as buyins from buy GROUP BY game_id,player_id;
CREATE VIEW 'game_winner' as select game_id,player_id as winner_id,profit from winner where share > 0.5;
CREATE VIEW 'game_runner' as select game_id,player_id as winner_id,profit from winner where share < 0.5;
CREATE VIEW 'game_buyins' as select game_id,sum(buyins) as allbuyins from playerbuyins group by game_id;
CREATE VIEW 'winner_share' as select game_buyins.game_id,game_buyins.allbuyins,game_winner.winner_id as player_id,(game_buyins.allbuyins -0.5)*.66 as winbuys from game_buyins LEFT JOIN game_winner on game_buyins.game_id = game_winner.game_id;
CREATE VIEW 'firstprize' as select player_id,sum(winbuys) as first_prize from winner_share group by player_id;
CREATE VIEW 'runner_share' as select game_buyins.game_id,game_buyins.allbuyins,game_runner.winner_id as player_id,(game_buyins.allbuyins -0.5)*.34 as winbuys from game_buyins LEFT JOIN game_runner on game_buyins.game_id = game_runner.game_id;
CREATE VIEW 'secondprize' as select player_id,sum(winbuys) as second_prize from runner_share group by player_id;
CREATE VIEW 'runner_totals' as select winner_id as player_id,count(winner_id) as second_totals from game_runner group by winner_id;
CREATE VIEW 'totals' as select player_id,count(player_id) as games_played ,sum(buyins) as total_buyins from playerbuyins group by player_id;
CREATE VIEW 'player_totals' as select player.id, player.name,games_played,total_buyins from player left join totals on player.id = totals.player_id;
CREATE VIEW 'winner_totals' as select winner_id as player_id,count(winner_id) as first_total from game_winner group by winner_id;
CREATE VIEW 'player_first' as select id,name,games_played,total_buyins,first_total as first from player_totals left join winner_totals on player_totals.id = winner_totals.player_id;
CREATE VIEW 'game_results' as select id,name,games_played,total_buyins,first,second_totals as second from player_first left join runner_totals on player_first.id = runner_totals.player_id;
CREATE VIEW 'game_first' as select id,name,games_played,total_buyins,first,second,first_prize from game_results left join firstprize on game_results.id = firstprize.player_id;
CREATE VIEW 'game_all' as select id,name,games_played,total_buyins,first,second,first_prize,second_prize from game_first left join secondprize on game_first.id = secondprize.player_id;
CREATE VIEW 'leaderboard' as select id,name,games_played,total_buyins,first,second, first_prize,second_prize,(ifnull(first_prize,0)+ifnull(second_prize,0)) as win_buyins, round((ifnull(first_prize,0)+ifnull(second_prize,0)) - total_buyins,2) as net_win, round((ifnull(first_prize,0)+ifnull(second_prize,0))/total_buyins,2) as strike_rate from game_all order by strike_rate desc;
CREATE VIEW 'check_sums' as select sum(total_buyins),sum(first),sum(second), sum(first_prize),sum(second_prize),sum(win_buyins), sum(net_win) from leaderboard order by strike_rate desc;