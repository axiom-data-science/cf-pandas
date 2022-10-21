"""
From cf-xarray.
"""

from collections import ChainMap

import pandas as pd

from .options import OPTIONS
from .utils import always_iterable, select_variables


@pd.api.extensions.register_dataframe_accessor("cf")
class CFAccessor:
    """Dataframe accessor analogous to cf-xarray accessor.

    Attributes
    ----------
    criteria : dict
        Custom vocabulary for selecting variables with regular expressions.
    """

    def __init__(self, pandas_obj):
        # self._validate(pandas_obj)
        self._obj = pandas_obj

    # @staticmethod
    # def _validate(obj):
    #     # verify there is a column latitude and a column longitude
    #     if "latitude" not in obj.columns or "longitude" not in obj.columns:
    #         raise AttributeError("Must have 'latitude' and 'longitude'.")

    @property
    def criteria(self):
        """Get custom criteria from options."""
        custom_criteria = ChainMap(*OPTIONS["custom_criteria"])
        # if criteria is None:
        #     if not OPTIONS["custom_criteria"]:
        #         return []
        #     criteria = OPTIONS["custom_criteria"]

        # if criteria is not None:
        #     criteria = always_iterable(criteria, allowed=(tuple, list, set))

        custom_criteria = always_iterable(custom_criteria, allowed=(tuple, list, set))
        custom_criteria = ChainMap(*custom_criteria)
        self._criteria = custom_criteria

        return self._criteria

    def __getitem__(self, key):
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

        col_name = select_variables(self._obj.columns.values, self.criteria, key)
        return self._obj[col_name]
