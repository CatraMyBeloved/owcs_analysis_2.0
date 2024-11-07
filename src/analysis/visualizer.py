import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels


class Visualizer:
    def __init__(self, data):
        self._id_vars = ['nickname', 'match_id', 'role', 'mode', 'map', 'duration', 'result']
        self._value_vars = ['eliminations', 'assists', 'deaths', 'kd_ratio', 'damage_dealt', 'healing_done',
                            'damage_mitigated', 'deaths_per_10', 'eliminations_per_10', 'assists_per_10',
                            'damage_dealt_per_10', 'healing_done_per_10', 'value']
        self._data = self._convert_to_long(data)
        self._filtered_data = self._data
        self._filter = None
        self.style_setup()

    def _convert_to_long(self, wide_data):
        long_data = pd.melt(wide_data, id_vars= self._id_vars, value_vars= self._value_vars, var_name=
                                               'stat_type', value_name='stat_value')
        return long_data
    def style_setup(self, style="darkgrid", context="talk", figsize = ()):
        sns.set_style(style)
        sns.set_context(context, font_scale=1.5)
        sns.despine()

    def filter_by(self, **kwargs):
        self._filtered_data = self._data.copy()
        for column, value in kwargs.items():
            self._filtered_data = self._filtered_data[self._filtered_data[column] == value]
        return self

    def basic_relationship(self, x_col, y_col, kind="scatter", title=None, hue=None, color="darkblue"):
        plt.figure(figsize=(12, 8))
        if hue:
            sns.relplot(data=self._filtered_data, kind=kind, x=x_col, y=y_col, hue=hue, color=color)
        else:
            sns.relplot(data=self._filtered_data, kind=kind, x=x_col, y=y_col, color=color)

        if title:
            plt.title(title)
        plt.tight_layout()
        plt.show()

    def regression(self, x_col, y_col, order=1, lowess=False, logx=False, title=None, hue=None, color="darkblue"):
        plt.figure(figsize=(12, 8))
        if hue:
            sns.regplot(data=self._filtered_data, x=x_col, y=y_col, order=order, lowess=lowess, logx=logx, color=color,
                        hue=hue)
        else:
            sns.regplot(data=self._filtered_data, x=x_col, y=y_col, order=order, lowess=lowess, logx=logx, color=color)

        if title:
            plt.title(title)
        plt.tight_layout()
        plt.show()

    def winrate(self, x_col = 'stat_value', n_bins=15, order=1, lowess=False, logx=False, title=None, hue=None, color="darkblue"):
        bins = pd.cut(self._filtered_data[x_col], n_bins)

        grouped_data = self._filtered_data.groupby(bins, observed=False )["result"].mean()

        x = pd.IntervalIndex(grouped_data.index).mid
        y = grouped_data.values
        plot_data = pd.DataFrame({"x": x, "y": y})
        plt.figure(figsize=(12, 8))
        if hue:
            sns.regplot(data=plot_data, x="x", y="y", order=order, lowess=lowess, logx=logx, hue=hue)
        else:
            sns.regplot(data=plot_data, x="x", y="y", order=order, lowess=lowess, logx=logx, color = color)

        if title:
            plt.title(title)
        plt.tight_layout()
        plt.ylim(bottom=0)
        plt.show()

    def simple_histogram(self, x_col = 'stat_value', n_bins = 15, title = None, hue = 'result',multiple = "layer", color="darkblue"):
        plt.figure(figsize=(12, 8))
        if hue:
            sns.histplot(data = self._filtered_data, x='stat_value', bins=n_bins, hue=hue, multiple = multiple)
        else:
            sns.histplot(data=self._filtered_data, x=x_col, bins=n_bins, color = color, multiple=multiple)

        if title:
            plt.title(title)
        plt.tight_layout()
        plt.show()

    def histogram_2d(self, x_col, y_col, n_bins = 15, title = None):
        plt.figure(figsize=(12, 12))
        sns.histplot(data = self._filtered_data, x=x_col, y=y_col, bins=n_bins)

        if title:
            plt.title(title)

        plt.tight_layout()
        plt.show()

