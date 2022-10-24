"""
From cf-xarray.
"""

import pandas as pd

import cf_pandas as cfp


@pd.api.extensions.register_dataframe_accessor("cf")
class CFAccessor:
    """Dataframe accessor analogous to cf-xarray accessor."""

    def __init__(self, pandas_obj):
        # self._validate(pandas_obj)
        self._obj = pandas_obj

    # @staticmethod
    # def _validate(obj):
    #     # verify there is a column latitude and a column longitude
    #     if "latitude" not in obj.columns or "longitude" not in obj.columns:
    #         raise AttributeError("Must have 'latitude' and 'longitude'.")

    def __getitem__(self, key: str):
        """Redefinition of dict-like behavior.
        This enables user to use syntax `reader[dataset_id]` to read in and
        save dataset into the object.
        Parameters
        ----------
        key: str
            dataset_id for a dataset that is available in the search/reader
            object.
        Returns
        -------
        xarray Dataset of the data associated with key
        """

        col_name = cfp.match_criteria_key(self._obj.columns.values, key)
        return self._obj[col_name]
