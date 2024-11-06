import logging

import numpy as np
import pandas as pd

from .maps import map_type_dict


class DataMuncher:
    """
    A class for processing and validating game match data.

    This class handles the extraction, transformation, and validating
    of match details and player statistics from game data.
    """

    def __init__(self):

        """
        Initialize the DataMuncher with empty data structures and set up logging.
        """

        self.details = []
        self.stats = []
        self.ex_details = []
        self.ex_stats = []
        self.matches_df = pd.DataFrame()
        self.player_dfs = {}
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.column_mapping = {
            "nickname": "nickname",
            'match_id': 'match_id',
            'Role': 'role',
            'Eliminations': 'eliminations',
            'Assists': 'assists',
            'Deaths': 'deaths',
            'K/D Ratio': 'kd_ratio',
            'Damage Dealt': 'damage_dealt',
            'Healing Done': 'healing_done',
            'Damage Mitigated': 'damage_mitigated',
            'Result': 'result',
            'mode': 'mode',
            'map': 'map'
        }

        self.team_dict = {}

        fh = logging.FileHandler('data_preparation.log')
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

    def add_data(self, details, stats):
        """
        Add data to the DataMuncher class for further extraction or validation.

        Args:
          details(list): Match details received from the FaceIT API
          stats(list): Match statistics received from the FaceIT API
        """
        self.stats.append(stats)
        self.details.append(details)
        return None

    def extract_stats(self):
        """
        Extracts match statistics from received data.

        Function to extract relevant data and collapse its nested structures.
        """
        for datapoint in self.stats:
            if not datapoint:
                self.logger.info(f"No match statistics available")
                datapoint = {}
                return None

            elif not isinstance(datapoint, dict):
                self.logger.info(f"Data was not provided in dictionary form.")
                self.datapoint = {}
                return

            else:

                rounds = datapoint.get("rounds")

                player_data = []

                try:

                    for match_round in rounds:
                        mode = match_round.get('round_stats', {}).get('OW2 Mode', "Unknown")
                        round_map = match_round.get('round_stats', {}).get('Map', "Unknown")
                        match_id = match_round.get('match_id', 0)
                        for team in match_round.get("teams", []):
                            players = team.get('players', [])
                            for player in players:
                                player_copy = player
                                player_copy['mode'] = mode
                                player_copy['map'] = round_map
                                player_copy['match_id'] = match_id
                                player_data.append(player_copy)

                    self.logger.info(f"Data successfully extracted.")
                    self.ex_stats.append(player_data)

                except Exception as e:
                    self.logger.error(f"Extraction of match statistics failed, {e}")
                    self.ex_stats.append({})

    def extract_details(self):
        """
        Extracts match details into easier format

        Function that reads in data, collapses nested data and extracts relevant data.
        """
        for datapoint in self.details:

            if not datapoint:
                self.logger.error(f"Match details were unavailable.")
                self.ex_details.append({})

            elif not isinstance(datapoint, dict):
                self.logger.error(f'Match details were not in dictionary form.')
                self.ex_details.append({})

            try:
                self.ex_details.append({
                    "match_id": datapoint.get("match_id"),
                    "competition_type": datapoint.get("competition_type"),
                    "competition_id": datapoint.get("competition_id"),
                    "competition_name": datapoint.get("competition_name"),
                    "started_at": datapoint.get("started_at"),
                    "finished_at": datapoint.get("finished_at"),
                    "winner": datapoint.get("results").get("winner"),
                    "faction_1": datapoint.get("teams").get("faction1").get("name"),
                    "faction_2": datapoint.get("teams").get("faction2").get("name"),
                    "faction_1_score": datapoint.get("results", {}).get("score", {}).get("faction1"),
                    "faction_2_score": datapoint.get("results", {}).get("score", {}).get("faction2"),
                    "maps": datapoint.get("voting", {}).get("map", {}).get("pick", []),
                    "map_types": [map_type_dict[x] for x in datapoint.get("voting", {}).get("map", {}).get("pick", [])],
                    "faction_1_map_scores": [results.get("factions", {}).get("faction1", {}).get("score", 0) for results
                                             in datapoint.get("detailed_results", [])],
                    "faction_2_map_scores": [results.get("factions", {}).get("faction2", {}).get("score", 0) for results
                                             in datapoint.get("detailed_results", [])],
                    "map_winner": [result.get("winner") for result in datapoint.get("detailed_results", [])]

                })
                self.logger.info(f'Extraction of match statistics succesful')
            except Exception as e:
                self.logger.error(f'Extraction of match details failed, {e}')

    def extract_all(self):
        """
        Simple helper function that extracts both details and stats.
        """
        self.logger.info(f'Starting match detail and statistics extraction.')
        self.extract_stats()
        self.extract_details()
        self.logger.info(f'Finished extraction')

    def prepare_data(self):
        """
        Transforms data and adds it to larger dataframes.

        Function to transform data into dataframes and add it to the larger dataframes containing all data.
        """
        try:
            self.matches_df = pd.concat([self.matches_df, pd.DataFrame(self.ex_details)])
            self.logger.info('Match details successfuly added, removing saved details.')
            self.details = []
            self.ex_details = []
        except Exception as e:
            self.logger.error(f'Addition of match details failed, {e}')
        try:
            for player in self.ex_stats[0]:

                nickname = player.get('nickname')
                map = player.get('map')
                mode = player.get('mode')
                match_id = player.get('match_id')
                new_row = {
                    'nickname': nickname,
                    'map': map,
                    'mode': mode,
                    'match_id': match_id,

                    **player.get('player_stats', {})
                }
                if nickname not in self.player_dfs:
                    self.player_dfs[nickname] = pd.DataFrame(columns=list(new_row.keys()))
                new_df = pd.DataFrame([new_row])
                self.player_dfs[nickname] = pd.concat([self.player_dfs[nickname], new_df], ignore_index=True)

            self.logger.info('Player stats successfuly added, removing saved stats.')
            self.stats = []
            self.ex_stats = []
        except Exception as e:
            self.logger.error(f'Addition of player data failed, {e}')

    def calculate_kd_ratio(self, dataframe):
        """
        Helper function to calculate KD-Ratio, as FaceIT data has problems here sometimes.
        """
        eliminations = dataframe['eliminations'].astype(int)
        deaths = dataframe['deaths'].astype(int)

        # Avoid division by zero
        kd_ratio = np.where(deaths == 0, eliminations, eliminations / deaths)

        return kd_ratio

    def rename_validate(self):
        """
        Renames columns and validates entries.

        Function to rename columns for easier upload to databank, renames columns, makes sure kd-ratio is correct and ensures correct types.
        """
        df = pd.DataFrame()
        for player_nickname, df_original in self.player_dfs.items():

            try:
                df = df_original.copy()
                df = df.rename(columns=self.column_mapping)

                self.logger.info('Renaming succesfull')
            except Exception as e:
                self.logger.error(f"Renaming failed, {e}")

            df['kd_ratio'] = self.calculate_kd_ratio(df)
            # check that all required columns are available, if not create them
            expected_names = list(self.column_mapping.values())
            for column in expected_names:
                if column not in df.columns:
                    self.logger.error(f"Missing column {column}, adding with default value")
                    df[column] = None

            # discard any unwanted columns
            df = df[expected_names]

            # make sure correct types are used in columns
            df["eliminations"] = df["eliminations"].astype(int)
            df["assists"] = df["assists"].astype(int)
            df["deaths"] = df["deaths"].astype(int)
            df["kd_ratio"] = df["kd_ratio"].astype(float)
            df["damage_dealt"] = df["damage_dealt"].astype(int)
            df["healing_done"] = df["healing_done"].astype(int)
            df["damage_mitigated"] = df["damage_mitigated"].astype(int)
            df["result"] = df["result"].astype(int)

            # fill nan
            df = df.fillna(0)

            self.player_dfs[player_nickname] = df
