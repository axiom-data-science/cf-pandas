"""
From cf-xarray.
"""

import itertools
from collections import ChainMap
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import pandas as pd
from pandas import DataFrame, Series

import cf_pandas as cfp

from .criteria import coordinate_criteria, guess_regex
from .options import OPTIONS
from .utils import (
    _is_datetime_like,
    always_iterable,
    match_criteria_key,
    set_up_criteria,
)
from .vocab import Vocab

#:  `axis` names understood by cf_xarray
_AXIS_NAMES = ("X", "Y", "Z", "T")

#:  `coordinate` types understood by cf_xarray.
_COORD_NAMES = ("longitude", "latitude", "vertical", "time")

# Type for Mapper functions
Mapper = Callable[[DataFrame, str], List[str]]


try:
    # delete the accessor to avoid warning
    del pd.DataFrame.cf
except AttributeError:
    pass


@pd.api.extensions.register_dataframe_accessor("cf")
class CFAccessor:
    """Dataframe accessor analogous to cf-xarray accessor."""

    def __init__(self, pandas_obj):
        # don't automatically validate but can when needed
        # self._validate(pandas_obj)
        self._obj = pandas_obj

    # @staticmethod
    def _validate(self):
        """what is necessary for basic use."""

        # verify that necessary keys are present. Z would also be nice but might be missing.
        # but don't use the accessor to check
        keys = ["T", "longitude", "latitude"]
        missing_keys = [
            key for key in keys if len(_get_axis_coord(self._obj, key)) == 0
        ]
        if len(missing_keys) > 0:
            raise AttributeError(
                f'{"longitude", "latitude", "time"} must be identifiable in DataFrame but {missing_keys} are missing.'
            )

        # for key in keys:
        #     if len(_get_axis_coord(obj, "T")) == 0:

        # if (len(_get_axis_coord(obj, "T")) == 0) or (len(_get_axis_coord(obj, "longitude")) == 0)

        # if not {"longitude", "latitude", "time"} <= obj.cf.coordinates():
        #     raise AttributeError(f'{"longitude", "latitude", "time"} must be identifiable in DataFrame but recognized keys are {obj.cf.keys()}.')

    def __getitem__(self, key: str) -> Union[pd.Series, pd.DataFrame]:
        """Select columns or columns by alias.

        If one column matches key, return a Series. Otherwise return a DataFrame.

        Parameters
        ----------
        key: str
            key in custom criteria/vocabulary to match with columns of DataFrame, or in axes or coordinates.

        Returns
        -------
        Series, DataFrame
            with matching column(s) included.

        Example
        -------
        >>> df.cf[alias]
        """

        # if key is a coordinate or axes, use a different method to match
        valid_keys = _COORD_NAMES + _AXIS_NAMES
        # return the key if it is already a name in the object and doesn't need to be interpreted
        if key in self._obj.keys():
            col_names = [key]

        elif key in valid_keys:
            col_names = _get_axis_coord(self._obj, key)

        else:
            col_names = _get_custom_criteria(self._obj, key)

        # return series for column
        if len(col_names) == 1 and col_names[0] in self._obj.columns:
            return self._obj[col_names[0]]
        # return index
        elif len(col_names) == 1 and col_names[0] in self._obj.index.names:
            return self._obj.index.get_level_values(col_names[0])
        # return DataFrame
        elif len(col_names) > 1:
            return self._obj[col_names]
        else:
            raise ValueError("Some error has occurred.")

    def __setitem__(self, key: str, values: Union[Sequence, Series]):
        """Set column by alias.

        Parameters
        ----------
        key: str
            key in custom criteria/vocabulary to match with columns of DataFrame, or in axes or coordinates.
        values : Union[Sequence, pd.Series]
            Values to set into object.

        Raises
        ------
        ValueError
            Can only set one column at once.
        """

        col = self.__getitem__(key)
        if isinstance(col, Series):
            self._obj[col.name] = values
            # return self._obj[col.name]
        elif col is None:
            # make new column
            self._obj[key] = values
            # return self._obj[key]
        elif isinstance(col, pd.Index):
            # which of possible multi index it is
            # does single and multi index need to be separated?
            # ilev = self._obj.index.names.index(col.name)
            # self._obj.index = self._obj.index.set_levels(values, level=ilev)

            # loop over levels in index so we know which level to replace
            inds = []
            for lev in range(self._obj.index.nlevels):
                ind = self._obj.index.get_level_values(lev)
                if self._obj.index.names[lev] == col.name:
                    save_type = type(col)
                    ind = save_type(values)
                    ind.name = col.name
                inds.append(ind)
            self._obj = self._obj.set_index(inds)

        else:
            raise ValueError("Setting item only works if key matches one column only.")

    def __contains__(self, item: str) -> bool:
        """
        Check whether item is a valid key for indexing with .cf
        """
        return item in self.keys()

    def keys(self) -> Set[str]:
        """
        Utility function that returns valid keys for .cf[].

        This is useful for checking whether a key is valid for indexing, i.e.
        that the attributes necessary to allow indexing by that key exist.

        Returns
        -------
        set
            Set of valid key names that can be used with __getitem__ or .cf[key].
        """

        varnames = list(self.axes) + list(self.coordinates)
        try:
            # see which custom keys have matched values in object
            matched_keys = [
                key for key, val in self.custom_keys.items() if len(val) > 0
            ]
            varnames.extend(matched_keys)
        except ValueError:
            # don't have criteria defined, then no custom keys to report
            pass
        # varnames.extend(list(self.cell_measures))
        # varnames.extend(list(self.standard_names))
        # varnames.extend(list(self.cf_roles))

        return set(varnames)

    @property
    def axes(self) -> Dict[str, List[str]]:
        """
        Property that returns a dictionary mapping valid Axis standard names for ``.cf[]``
        to variable names.

        This is useful for checking whether a key is valid for indexing, i.e.
        that the attributes necessary to allow indexing by that key exist.
        It will return the Axis names ``("X", "Y", "Z", "T")``
        present in ``.columns``.

        Returns
        -------
        dict
            Dictionary with keys that can be used with ``__getitem__`` or as ``.cf[key]``.
            Keys will be the appropriate subset of ("X", "Y", "Z", "T").
            Values are lists of variable names that match that particular key.
        """
        # vardict = {key: self.__getitem__(key) for key in _AXIS_NAMES}
        vardict = {key: _get_all(self._obj, key) for key in _AXIS_NAMES}
        return {k: sorted(v) for k, v in vardict.items() if v}

    @property
    def coordinates(self) -> Dict[str, List[str]]:
        """
        Property that returns a dictionary mapping valid Coordinate standard names for ``.cf[]``
        to variable names.

        This is useful for checking whether a key is valid for indexing, i.e.
        that the attributes necessary to allow indexing by that key exist.
        It will return the Coordinate names ``("latitude", "longitude", "vertical", "time")``
        present in ``.columns``.

        Returns
        -------
        dict
            Dictionary of valid Coordinate names that can be used with ``__getitem__`` or ``.cf[key]``.
            Keys will be the appropriate subset of ``("latitude", "longitude", "vertical", "time")``.
            Values are lists of variable names that match that particular key.
        """
        # vardict = {key: self.__getitem__(key) for key in _COORD_NAMES}
        vardict = {key: _get_all(self._obj, key) for key in _COORD_NAMES}

        return {k: sorted(v) for k, v in vardict.items() if v}

    @property
    def custom_keys(self):
        """
        Returns a dictionary mapping criteria keys to variable names.

        Returns
        -------
        dict
            Dictionary mapping criteria keys to variable names.

        Notes
        -----
        Need to use this with context manager version of providing custom_criteria.
        """

        custom_criteria = set_up_criteria()
        vardict = {
            key: _get_custom_criteria(self._obj, key) for key in custom_criteria.keys()
        }

        return vardict

    @property
    def axes_cols(self) -> List[str]:
        """
        Property that returns a list of column names from the axes mapping.

        Returns
        -------
        list
            Variable names that are the column names which represent axes.
        """

        return list(itertools.chain(*[*self.axes.values()]))

    @property
    def coordinates_cols(self) -> List[str]:
        """
        Property that returns a list of column names from the coordinates mapping.

        Returns
        -------
        list
            Variable names that are the column names which represent coordinates.
        """

        return list(itertools.chain(*[*self.coordinates.values()]))

    @property
    def standard_names(self):
        """
        Returns a dictionary mapping standard_names to variable names, if there is a match. Compares with all cf-standard names.

        Returns
        -------
        dict
            Dictionary mapping standard_names to variable names.

        Notes
        -----
        This is not the same as the cf-xarray accessor method of the same name, which searches for variables with standard_name attributes and surfaces those values to map to the variable name.
        """

        names = cfp.standard_names()

        vardict = {}
        for key in names:
            local_criteria = Vocab().make_entry(key, f"{key}$")
            key_match = _get_custom_criteria(
                self._obj, key, criteria=local_criteria.vocab
            )

            if len(key_match) > 0:
                vardict[key] = key_match

        return vardict


def _get_axis_coord(obj: Union[DataFrame, Series], key: str) -> list:
    """
    Translate from axis or coord name to variable name. After matching based on coordinate_criteria,
    if there are no matches for key, then guess_regex is used to search for matches.

    Parameters
    ----------
    obj : DataArray, Dataset
        DataArray belonging to the coordinate to be checked
    key : str, ["X", "Y", "Z", "T", "longitude", "latitude", "vertical", "time"]
        key to check for.

    Returns
    -------
    List[str], Variable name(s) in parent xarray object that matches axis or coordinate `key`

    Notes
    -----
    This functions checks for the following attributes in order
    - `standard_name` (CF option)
    - `_CoordinateAxisType` (from THREDDS)
    - `axis` (CF option)
    - `positive` (CF standard for non-pressure vertical coordinate)

    References
    ----------
    MetPy's parse_cf
    """

    valid_keys = _COORD_NAMES + _AXIS_NAMES
    if key not in valid_keys:
        raise KeyError(
            f"cf_xarray did not understand key {key!r}. Expected one of {valid_keys!r}"
        )

    # loop over column names and index names
    results: set = set()
    cols_and_indices = list(obj.columns)
    cols_and_indices += obj.index.names
    # remove None if in names from index
    cols_and_indices = [name for name in cols_and_indices if name is not None]
    for col in cols_and_indices:
        if key in coordinate_criteria:
            for criterion, expected in coordinate_criteria[key].items():
                # allow for the column header having a space in it that separate
                # the name from the units, for example
                strings = col.split()
                for string in strings:
                    string = string.lower()
                    if string.startswith("(") and string.endswith(")"):
                        if string.strip(")(") in expected:
                            results.update((col,))
                    if string in expected:
                        # if col.attrs.get(criterion, None) in expected:
                        results.update((col,))
                    # if criterion == "units":
                    #     # deal with pint-backed objects
                    #     units = getattr(col.data, "units", None)
                    #     if units in expected:
                    #         results.update((col,))
        # also use the guess_regex approach by default, but only if no results so far
        # this takes the logic from cf-xarray guess_coord_axis
        if len(results) == 0:
            if col in obj.columns:
                if key in ("T", "time") and _is_datetime_like(obj[col]):
                    results.update((col,))
                    continue  # prevent second detection
            elif col in obj.index.names:
                if key in ("T", "time") and _is_datetime_like(
                    obj.index.get_level_values(col)
                ):
                    results.update((col,))
                    continue  # prevent second detection
            pattern = guess_regex[key]
            if pattern.match(col.lower()):
                results.update((col,))

    return list(results)


def _get_all(obj: DataFrame, key: str) -> List[str]:
    """
    One or more of ('X', 'Y', 'Z', 'T', 'longitude', 'latitude', 'vertical', 'time',
    'area', 'volume'), or arbitrary measures, or standard names
    """
    all_mappers = (
        _get_custom_criteria,
        # functools.partial(_get_custom_criteria, criteria=cf_role_criteria),
        _get_axis_coord,
        # _get_measure,
        # _get_with_standard_name,
    )
    results = apply_mapper(all_mappers, obj, key, error=False, default=None)
    return list(set(results))


def apply_mapper(
    mappers: Union[Mapper, Tuple[Mapper, ...]],
    obj: DataFrame,
    key: Hashable,
    error: bool = True,
    default: Any = None,
) -> List[Any]:
    """
    Applies a mapping function; does error handling / returning defaults.
    Expects the mapper function to raise an error if passed a bad key.
    It should return a list in all other cases including when there are no
    results for a good key.
    """

    if not isinstance(key, Hashable):
        if default is None:
            raise ValueError(
                "`default` must be provided when `key` is not not a valid DataArray name (of hashable type)."
            )
        return list(always_iterable(default))

    default = [] if default is None else list(always_iterable(default))

    def _apply_single_mapper(mapper):

        try:
            results = mapper(obj, key)
        except (KeyError, ValueError) as e:
            if error or "I expected only one." in repr(e):
                raise e
            else:
                results = []
        return results

    if not isinstance(mappers, Iterable):
        mappers = (mappers,)

    # apply a sequence of mappers
    # if the mapper fails, it *should* return an empty list
    # if the mapper raises an error, that is processed based on `error`
    results = []
    for mapper in mappers:
        results.append(_apply_single_mapper(mapper))

    flat = list(itertools.chain(*results))
    # # de-duplicate
    # if all(not isinstance(r, DataArray) for r in flat):
    #     results = list(set(flat))
    # else:
    #     results = flat
    results = flat

    nresults = any(bool(v) for v in [results])
    if not nresults:
        if error:
            raise KeyError(
                f"cf-xarray cannot interpret key {key!r}. Perhaps some needed attributes are missing."
            )
        else:
            # none of the mappers worked. Return the default
            return default
    return results


# Already use match_criteria_key in other functions, and it is a bit more generic so can be used
# without accessor.
def _get_custom_criteria(obj: DataFrame, key: str, criteria=None) -> List[str]:

    results = match_criteria_key(obj.columns, key, criteria, split=True)
    return results
