import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class Visualizer:
    def __init__(self, data):
        self._data = data
        self._filtered_data = data
        self._filter = None
        self.style_setup()

    def style_setup(self, style="darkgrid", context="talk"):
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

    def winrate(self, x_col, n_bins=15, order=1, lowess=False, logx=False, title=None, hue=None, color="darkblue"):
        bins = pd.cut(self._filtered_data[x_col], n_bins)

        grouped_data = self._filtered_data.groupby(bins)["result"].mean()

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
        plt.show()

    def simple_histogram(self, x_col, n_bins = 15, title = None, hue = 'result',multiple = "layer", color="darkblue"):
        if hue:
            sns.histplot(data = self._filtered_data, x=x_col, bins=n_bins, hue=hue, multiple = multiple)
        else:
            sns.histplot(data=self._filtered_data, x=x_col, bins=n_bins, color = color, multiple=multiple)

        if title:
            plt.title(title)
        plt.tight_layout()
        plt.show()

    def histogram_2d(self, x_col, y_col, n_bins = 15, title = None):
        sns.histplot(data = self._filtered_data, x=x_col, y=y_col, bins=n_bins)

        if title:
            plt.title(title)

        plt.tight_layout()
        plt.show()

