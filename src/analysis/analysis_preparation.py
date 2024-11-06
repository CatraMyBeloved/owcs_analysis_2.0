import ast
import logging
from operator import add

import numpy as np
import pandas as pd


class AnalysisPreparation:
    """
    A class for preparing and beginning first analysis on player and match data.

    This class handles data preprocessing, stat calculations, and various adjustments
    for analyzing player performance across different roles and map types.

    Attributes:
        player_data (DataFrame): DataFrame containing player-specific data.
        match_data (DataFrame): DataFrame containing match-specific data.
        stat_weights (np.array): Weights for different player statistics.
        match_ids (set): Set of unique match IDs.
        stat_weight_adjustment (dict): Role-specific stat weight adjustments.
        death_threshold (int): Threshold for death penalty calculation.
        death_steepness (float): Steepness factor for death penalty calculation.
        columns_to_derive (list): List of columns for which to calculate per-10-minute stats.
        logger (logging.Logger): Logger for the class.
    """

    def __init__(self, player_data, match_data):
        """
        Initialize the AnalysisPreparation object.

        Args:
            player_data (DataFrame): DataFrame containing player-specific data.
            match_data (DataFrame): DataFrame containing match-specific data.
        """
        self.player_data = player_data
        self.match_data = match_data
        self.stat_weights = np.array([2, 0.5, 0.001, 0.001, 1])
        self.match_ids = set(match_data['match_id'])
        self.stat_weight_adjustment = {
            'Tank': np.array([1.2, 1, 1, 0, 1.2]),
            'Damage': np.array([1.2, 1, 1.2, 0, 1]),
            'Support': np.array([1, 1.2, 1, 1.2, 1.2])
        }

        self.death_threshold = 7
        self.death_steepness = 0.5

        self.columns_to_derive = ['deaths', 'eliminations', 'assists', 'damage_dealt', 'healing_done']

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler('AnalysisPreparation.log')
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

        # Convert string representations to Python objects
        self._convert_string_to_list(['faction_1_map_scores', 'faction_2_map_scores', 'maps', 'map_types'])

    def _drop_nan_rows(self):

        boolean = self.match_data.isna().any(axis=1)

        rows_with_nan = self.match_data[boolean]

        ids_to_drop = rows_with_nan['match_id']

        self.match_data = self.match_data[~self.match_data['match_id'].isin(ids_to_drop)]
        self.player_data = self.player_data[~self.player_data['match_id'].isin(ids_to_drop)]

    def _convert_string_to_list(self, columns):
        """
        Convert string representations of lists to actual Python lists for specified columns.

        Args:
            columns (list): List of column names to convert.
        """
        for column in columns:
            self.match_data[column] = self.match_data[column].apply(ast.literal_eval)

    def add_duration(self):
        """
        Calculate and add the duration of each match to the match_data.

        The duration is calculated as 90% of the time difference between finished_at and started_at.
        """
        try:
            self.match_data['duration'] = ((self.match_data['finished_at'] - self.match_data['started_at']) * 0.9)
        except Exception as e:
            self.logger.error(f'Adding duration failed. {e}')

    def adjust_points(self):

        self._drop_nan_rows()

        def adjust_scores(row):
            map_types = row['map_types']
            faction_1_scores = row['faction_1_map_scores']
            faction_2_scores = row['faction_2_map_scores']

            type_factor_control = [2 if map_type == 'Control' else 1 for map_type in map_types]

            adjusted_faction_1 = [score * factor for score, factor in zip(faction_1_scores, type_factor_control)]
            adjusted_faction_2 = [score * factor for score, factor in zip(faction_2_scores, type_factor_control)]

            type_factor_hybrid = [1 if map_type == 'Hybrid' else 0 for map_type in map_types]

            adjusted_faction_1 = [score + factor for score, factor in zip(adjusted_faction_1, type_factor_hybrid)]
            adjusted_faction_2 = [score + factor for score, factor in zip(adjusted_faction_2, type_factor_hybrid)]

            return pd.Series({'faction_1_map_scores': adjusted_faction_1,
                              'faction_2_map_scores': adjusted_faction_2})

        adjusted_scores = self.match_data.apply(adjust_scores, axis=1)

        self.match_data.loc[:, 'faction_1_map_scores'] = adjusted_scores['faction_1_map_scores']
        self.match_data.loc[:, 'faction_2_map_scores'] = adjusted_scores['faction_2_map_scores']

    def calculate_round_duration(self):
        """
        Calculate the duration of each round for every match and player.

        This method distributes the total match duration among rounds based on the points scored in each round.
        """
        match_ids = set(self.player_data.loc[:, 'match_id'])

        self.player_data['duration'] = np.nan

        match_data_filtered = self.match_data[self.match_data['match_id'].isin(match_ids)]
        match_data_filtered = match_data_filtered.set_index('match_id')

        for match_id in match_ids:
            match_row = match_data_filtered.loc[match_id]

            team_1_points = match_row['faction_1_map_scores']
            team_2_points = match_row['faction_2_map_scores']

            sum_points = sum(team_1_points) + sum(team_2_points)

            duration = int(match_row['duration'])

            map_types = match_row['map_types']
            # Calculate duration for each round based on points scored
            round_durations = [x / sum_points * duration for x in map(add, team_1_points, team_2_points)]

            match_players_bool = self.player_data['match_id'] == match_id
            match_players = set(self.player_data.loc[match_players_bool, 'nickname'])

            for player in match_players:
                player_bool = match_players_bool & (self.player_data['nickname'] == player)

                player_maps = self.player_data.loc[player_bool, :].loc[:, 'mode']

                mask = pd.Series(map_types).isin(player_maps)[:len(team_1_points)]

                filtered_durations = np.array(round_durations)[mask]

                filtered_durations = filtered_durations.tolist()
                self.player_data.loc[player_bool, 'duration'] = filtered_durations

    def validate_durations(self):

        def _is_valid_duration(row):
            return row['duration'] > ((sum(row['faction_1_map_scores']) + sum(row['faction_2_map_scores'])) * 120)

        boolean = self.match_data.apply(_is_valid_duration, axis=1)

        rows_with_valid_durations = self.match_data[boolean]

        ids_to_keep = rows_with_valid_durations['match_id']

        self.match_data = self.match_data[self.match_data['match_id'].isin(ids_to_keep)]
        self.player_data = self.player_data[self.player_data['match_id'].isin(ids_to_keep)]

    def calculate_derived(self):
        """
        Calculate derived statistics (per 10 minutes) for specified columns.

        This method calculates per-10-minute stats for deaths, eliminations, assists, damage dealt, and healing done.
        """
        for column in self.columns_to_derive:
            self.player_data[f'{column}_per_10'] = np.nan
            self.player_data[f'{column}_per_10'] = self.player_data.apply(
                lambda x: x[column] * 10 / (x['duration'] / 60), axis=1
            )

    def _value_function(self, row):

        role = row['role']
        weights = np.array([2, 0.5, 0.001, 0.001, 1])

        weight_adjustment = {
            'Tank': np.array([1.2, 1, 1, 0, 1.2]),
            'Damage': np.array([1.2, 1, 1.18, 0, 1.2]),
            'Support': np.array([1.1, 1.2, 1, 1.3, 1.15])
        }

        weights = weight_adjustment.get(role, np.ones([5])) * weights

        stats = np.array([row['eliminations_per_10'], row['assists_per_10'], row['damage_dealt'], row['healing_done'],
                          row['deaths']])

        weighted_stats = weights * stats

        result = np.sum(weighted_stats[0:4])

        death_threshold = 7

        death_steepness = 0.5

        death_penalty = (1 / (1 + np.exp(-death_steepness * (weighted_stats[4] - death_threshold)))) * 30

        final_value = result - death_penalty

        return final_value

    def calculate_value(self):

        self.player_data['value'] = self.player_data.apply(self._value_function, axis=1)

    def pipeline_helper(self):
        self.add_duration()
        self.adjust_points()
        self.calculate_round_duration()
        self.calculate_derived()
        self.calculate_value()
