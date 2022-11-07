"""
Utilities for cf-pandas.
"""

from collections import ChainMap
from typing import Any, Iterable, Optional, Union

import pandas as pd
import regex

from .options import OPTIONS


def always_iterable(obj: Any, allowed=(tuple, list, set, dict)) -> Iterable:
    """This is from cf-xarray."""
    return [obj] if not isinstance(obj, allowed) else obj


def astype(value, type_):
    """Return `value` as type `type_`.
    Particularly made to work correctly for returning string, `PosixPath`, or `Timestamp` as list.
    """

    if not isinstance(value, type_):
        import pathlib

        if type_ == list and isinstance(value, (str, pathlib.PurePath, pd.Timestamp)):
            return [value]
        return type_(value)
    return value


def set_up_criteria(criteria: Union[dict, Iterable] = None) -> ChainMap:
    """Get custom criteria from options.

    Parameters
    ----------
    criteria : dict, optional
        Criteria to use to map from variable to attributes describing the variable. If user has defined
        custom_criteria, this will be used by default.

    Returns
    -------
    ChainMap
        Criteria
    """

    if criteria is None:
        if not OPTIONS["custom_criteria"]:
            raise ValueError(
                "criteria needs to be defined either using set_options or directly input."
            )
        criteria_it = OPTIONS["custom_criteria"]
    else:
        criteria_it = always_iterable(criteria, allowed=(tuple, list, set))

    return ChainMap(*criteria_it)


def match_criteria_key(
    available_values: list,
    keys_to_match: Union[str, list],
    criteria: Optional[dict] = None,
) -> list:
    """Use criteria to choose match to key from available available_values.

    Parameters
    ----------
    available_values: list
        String or list of strings to compare against list of category values. They should be keys in `criteria`.
    keys_to_match : str, list
        Key(s) from criteria to match with available_values.
    criteria : dict, optional
        Criteria to use to map from variable to attributes describing the variable. If user has defined custom_criteria, this will be used by default.

    Returns
    -------
    list
        Values from available_values that match keys_to_match, according to criteria.

    Notes
    -----
    This uses logic from `cf-xarray`.
    """

    custom_criteria = set_up_criteria(criteria)

    keys_to_match = astype(keys_to_match, list)
    results = []
    for key in keys_to_match:

        if custom_criteria is not None and key in custom_criteria:
            # criterion is the attribute type — in this function we don't use it,
            # instead we use all the patterns available in criteria to match with available_values
            for criterion, patterns in custom_criteria[key].items():
                results.extend(
                    list(
                        set(
                            [
                                value
                                for value in available_values
                                if regex.match(patterns, value)
                            ]
                        )
                    )
                )

        # catch scenario that user input valid reader variable names
        else:
            if key in available_values:
                results.append(key)
    return list(set(results))


def standard_names():
    """Returns list of CF standard_names.

    Returns
    -------
    list
        All CF standard_names
    """

    import requests
    from bs4 import BeautifulSoup

    url = "https://cfconventions.org/Data/cf-standard-names/79/src/cf-standard-name-table.xml"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, features="xml")

    standard_names = [entry.get("id") for entry in soup.find_all("entry")]

    return standard_names
