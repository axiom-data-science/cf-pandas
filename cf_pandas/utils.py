"""
Utilities for cf-pandas.
"""

import pathlib

from typing import Any, Iterable

import pandas as pd
import regex


def always_iterable(obj: Any, allowed=(tuple, list, set, dict)) -> Iterable:
    """This is from cf-xarray."""
    return [obj] if not isinstance(obj, allowed) else obj


def astype(value, type_):
    """Return `value` as type `type_`.
    Particularly made to work correctly for returning string, `PosixPath`, or `Timestamp` as list.
    """
    import pathlib

    if not isinstance(value, type_):
        if type_ == list and isinstance(value, (str, pathlib.PurePath, pd.Timestamp)):
            return [value]
        return type_(value)
    return value


def select_variables(variable_strings, criteria, nicknames):
    """Use variable criteria to choose from available variables.
    Parameters
    ----------
    server: str
        Information for the reader, as follows:
        * For an ERDDAP reader, `server` should be the ERDDAP server
          input as a string. For example, http://erddap.sensors.ioos.us/erddap.
        * For the axds reader, `server` should just be 'axds'. Note that
          the variable list is only valid for `axds_type=='platform2'`, not for
          'layer_group'
    criteria: dict, str
        Custom criteria input by user to determine which variables to select.
    variables: string, list
        String or list of strings to compare against list of valid
        variable names. They should be keys in `criteria`.
    Returns
    -------
    Variables from server that match with inputs. UPDATE ALL
    Notes
    -----
    This uses logic from `cf-xarray`.
    """

    nicknames = astype(nicknames, list)
    results = []
    for key in nicknames:

        if criteria is not None and key in criteria:
            for criterion, patterns in criteria[key].items():
                results.extend(
                    list(
                        set(
                            [
                                var
                                for var in variable_strings
                                if regex.match(patterns, var)
                            ]
                        )
                    )
                    #                     list(set([var for var in variable_strings if re.match(patterns, var)]))
                )

        # catch scenario that user input valid reader variable names
        else:
            #             check_variables(server, nicknames)
            if key in variable_strings:
                results.append(key)
    return list(set(results))
