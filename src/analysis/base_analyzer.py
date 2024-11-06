class BaseAnalyzer:

    def __init__(self, player_data, match_data, team_dict):
        self.player_data = player_data
        self.match_data = match_data
        self.team_dict = team_dict
        self._identifier_variables = ['nickname', 'match_id', 'role', 'mode', 'map', 'duration', 'result']
        self._value_variables = ['eliminations', 'assists', 'deaths', 'kd_ratio', 'damage_dealt', 'healing_done',
                                 'damage_mitigated', 'deaths_per_10', 'eliminations_per_10', 'assists_per_10',
                                 'damage_dealt_per_10', 'healing_done_per_10', 'value']
        self._standard_comparison = ['eliminations_per_10', 'assists_per_10', 'deaths_per_10', 'damage_dealt_per_10',
                                     'healing_done_per_10']
        self._long_data = self._convert_to_long_format()

    def select_players(self, player_names):
        return self.player_data[self.player_data['nickname'].isin(player_names)]

    def select_team(self, team_name):
        team_players = self.team_dict[team_name]

        return self.select_players(team_players)

    def _convert_to_long_format(self, stats_to_convert=None):
        long_data = self.player_data.melt(id_vars=self._identifier_variables,
                                          value_vars=self._value_variables,
                                          var_name='stat_type',
                                          value_name='stat_value')

        return long_data

    def export_for_r_analysis(self, filepath):
        """Export prepared data for R analysis"""
        self._long_data.to_csv(filepath, index=False)
