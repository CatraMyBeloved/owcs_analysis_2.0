import matplotlib.pyplot as plt
import seaborn as sns

from .base_analyzer import BaseAnalyzer


class Visualizer(BaseAnalyzer):

    def __init__(self, player_data, match_data, team_dict):
        super().__init__(player_data, match_data, team_dict)

    def plot_player_stats(self, player_name, stats_to_compare=None):

        if stats_to_compare is None:
            stats_to_compare = self._standard_comparison

        filtered_data = self._long_data[(self._long_data['nickname'] == player_name) &
                                        (self._long_data['stat_type'].isin(stats_to_compare))
                                        ]
        grid = sns.FacetGrid(data=filtered_data,
                             col='stat_type',
                             col_wrap=3,
                             height=5,
                             aspect=1.5)

        grid.map(
            sns.boxplot,
            'result',
            'value'
        )

        grid.fig.suptitle(f'Stats for {player_name}')
        grid.set_titles('{col_name} Stats')
        grid.set_axis_labels('Result', 'Value')
        plt.tight_layout()

        return grid

    def compare_player_stats(self, player_names, stats_to_compare=None):

        if stats_to_compare is None:
            stats_to_compare = self._standard_comparison

        filtered_data = self._long_data[(self._long_data['nickname'].isin(player_names)) &
                                        (self._long_data['stat_type'].isin(stats_to_compare))
                                        ]

        grid = sns.FacetGrid(filtered_data, col='stat_type', col_wrap=3, height=5, aspect=1.5)

        grid.map(
            sns.boxplot,
            'nickname',
            'value',
            'result'
        )

        grid.fig.suptitle(f'Comparison for {player_names}')

        grid.set_titles('{col_name}')
        grid.set_axis_labels('Player', 'Value')

        return grid

    def plot_averages(self, player_names, stats_to_plot=None):

        if stats_to_plot is None:
            stats_to_plot = self._standard_comparison

        filtered_data = self._long_data[(self._long_data['nickname'].isin(player_names)) &
                                        (self._long_data['stat_type'].isin(stats_to_plot))
                                        ]

        grid = sns.FacetGrid(filtered_data, col='stat_type', col_wrap=3, height=5, aspect=1.5, sharey=False)

        grid.map(sns.barplot, 'nickname', 'value')

        return grid
