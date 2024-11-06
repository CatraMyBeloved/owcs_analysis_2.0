import json
import logging
import os
import sqlite3

import pandas as pd


class DatabaseManager:

    def __init__(self, database_file, base_path = "data"):
        self.database_file = database_file
        self.base_path = base_path
        self.database_file_path = os.path.join(base_path, database_file)
        self.database_connection = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler('database_management.log')
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

    def setup_connection(self):

        os.makedirs(self.base_path, exist_ok=True)

        if not os.path.exists(f'{self.database_file_path}'):
            self.logger.error(f"Database file not available, creating new one at {self.database_file_path}")

            try:
                self.database_connection = sqlite3.connect(f'{self.database_file_path}')
                self.logger.info(f'Database created and connected.')

                cursor = self.database_connection.cursor()
                try:
                    cursor.execute('''CREATE TABLE IF NOT EXISTS matches(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT,
            competition_type TEXT,
            competition_id TEXT,
            competition_name TEXT,
            started_at INT,
            finished_at INT,
            winner TEXT,
            faction_1_score INT,
            faction_2_score INT,
            faction_1 TEXT,
            faction_2 TEXT,
            maps TEXT,
            map_types TEXT,
            faction_1_map_scores INT,
            faction_2_map_scores INT,
            map_winner TEXT
            )''')

                    cursor.execute('''CREATE TABLE IF NOT EXISTS players(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT,
            match_id TEXT,
            role TEXT,
            eliminations INT,
            assists INT,
            deaths INT,
            kd_ratio REAL,
            damage_dealt INT,
            healing_done INT,
            damage_mitigated INT,
            result INT,
            mode TEXT,
            map TEXT,

            FOREIGN KEY (match_id) REFERENCES matches(match_id))
            ''')

                    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_player_nickname ON players(nickname)''')
                    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_match_id ON players(match_id)''')
                    self.logger.info('Tables created.')
                except sqlite3.Error as e:
                    self.logger.error(f'Failed to create tables, {e}')

            except sqlite3.Error as e:
                self.logger.error(f"Failed to create database, {e}")

        else:
            self.logger.info("File found, establishing connection.")

            try:
                self.database_connection = sqlite3.connect(f'{self.database_file_path}')
                self.logger.info('Established connection')

            except sqlite3.Error as e:
                self.logger.error(f"Connection failed, {e}")
        return None

    def query(self, query):

        if not self.database_connection:
            self.logger.error('No connection to database')
            return pd.DataFrame({})

        try:
            response = pd.read_sql(query, self.database_connection)
            self.logger.info('Successful query')
        except sqlite3.Error as e:
            response = pd.DataFrame({})
            self.logger.error(f'query unsuccessful, {e}')
        return response

    def delete_database(self):
        if input(f"Are you sure you want to delete the file {self.database_file_path}? (y/n)") == "y":
            try:
                os.remove(f"{self.database_file_path}")
                self.logger.info(f"File {self.database_file_path} successfuly deleted")
            except Exception as e:
                self.logger.error(f"Deletion unsuccessful, {e}")
        else:
            self.logger.info(f"Process aborted, no files were deleted")

    def dump_to_json(self, file):
        return json.dumps(file)

    def upload_match_details(self, match_data):
        """
        Uploads match data to database.
        Dumps rows containing lists into json strings, as sql does not accept lists. Then attempts to upload to database.
        """
        json_columns = ['maps', 'map_types', 'faction_1_map_scores', 'faction_2_map_scores', 'map_winner', ]

        for col in json_columns:
            match_data[col] = match_data[col].apply(self.dump_to_json)
        try:
            match_data.to_sql("matches", self.database_connection, if_exists="append", index=False)
            self.database_connection.commit()
            self.logger.info(f"Upload successfull")
        except sqlite3.Error as e:
            self.database_connection.rollback()
            self.logger.error(f"Upload unsuccessfull, {e}")

    def upload_player_data(self, player_dfs):
        """
        Uploads and appends new player data.
        Tries to turn each player dataframe from player_data_dict into entries into the player table in the database. Prints error if unsuccessful.
        """
        try:
            for player_nickname, df in player_dfs.items():
                df.to_sql("players", self.database_connection, if_exists="append", index=False)
            self.database_connection.commit()
            self.logger.info(f"Upload successfull")
        except sqlite3.Error as e:
            self.database_connection.rollback()
            self.logger.error(f"Upload unsuccessfull, {e}")
