import pandas as pd

from sklearn.preprocessing import StandardScaler, MinMaxScaler


class BaseAnalysis:
    def __init__(self):
        self._id_variables = ['nickname', 'match_id', 'role', 'mode', 'map', 'duration', 'result']
        self._original_data = pd.DataFrame()  # long format
        self._processed_data = pd.DataFrame()  # long format
        self._processed_data_wide = pd.DataFrame()  # wide format
        self.Scaler = StandardScaler()
        self.MinMaxScaler = MinMaxScaler()
        return

    def add_data(self, data, data_type="wide"):
        if data_type == "wide":
            pivoted_data = self._wide_to_long()
            self._original_data = self._original_data.append(pivoted_data)
        elif data_type == "long":
            self._original_data = self._original_data.append(data)
        return self

    def _handle_missing_values(self):
        self._processed_data = self._original_data.fillna(0)
        return

    def _validate_data(self):
        pass

    def _wide_to_long(self, data):
        return pd.melt(data, id_vars=self._id_variables, var_name="stat_type", value_name="stat_value")

    def _long_to_wide(self, data):
        return pd.pivot_table(data, columns='stat_type', values='stat_value')

    def prepare_data(self):
        # Scale data, handle missing values, maybe small validation?
        self._handle_missing_values()
        scaler = StandardScaler()
        temp_wide = self._long_to_wide(self._processed_data)

        columns_to_scale = [column for column in temp_wide.columns if column not in self._id_variables]

        temp_wide[columns_to_scale] = scaler.fit_transform(temp_wide[columns_to_scale])

        self._processed_data = self._wide_to_long(temp_wide)

        self._validate_data()
        self._processed_data_wide = self._long_to_wide(self._processed_data)
        return self

    def filter_by(self, **kwargs):
        pass
