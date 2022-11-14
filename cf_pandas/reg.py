"""Class for writing regular expressions."""

from typing import List, Optional, Sequence, Type, Union

from .utils import astype


class Reg(object):
    """Class to write a regular expression.

    Notes
    -----
    * Input strings are never allowed to be empty.
    * Need escape characters on any special characters, and then convert to raw, e.g., r"\[celsius\]" for "[celsius]".
    * The `exclude` options are logical "or".
    * The `include` option is logical "and", `include_or` is logical "or", and the other `include_` options allow for only one selection. If you want to use more than one `include_start` for example, you should make an additional regular expression.
    """

    def __init__(
        self,
        exclude: Optional[Union[List[str], str]] = None,
        exclude_start: Optional[Union[List[str], str]] = None,
        exclude_end: Optional[Union[List[str], str]] = None,
        include: Optional[Union[List[str], str]] = None,
        include_or: Optional[Union[List[str], str]] = None,
        include_exact: Optional[str] = None,
        include_start: Optional[str] = None,
        include_end: Optional[str] = None,
        ignore_case: bool = True,
    ):

        self._exclude = (
            [] if exclude is None or exclude == "" else astype(exclude, list)
        )
        self._exclude_start = (
            []
            if exclude_start is None or exclude_start == ""
            else astype(exclude_start, list)
        )
        self._exclude_end = (
            []
            if exclude_end is None or exclude_start == ""
            else astype(exclude_end, list)
        )
        self._include = (
            [] if include is None or include == "" else astype(include, list)
        )
        self._include_or = (
            [] if include_or is None or include_or == "" else astype(include_or, list)
        )
        self._include_exact = (
            "" if include_exact is None or include_exact == "" else include_exact
        )
        self._include_start = (
            "" if include_start is None or include_start == "" else include_start
        )
        self._include_end = (
            "" if include_end is None or include_end == "" else include_end
        )

        self.ignore_case = ignore_case

        self.check()

    def check(self):
        """Check to make sure selected options are compatible."""

        others = [
            self._exclude,
            self._exclude_start,
            self._exclude_end,
            self._include,
            self._include_or,
            self._include_end,
            self._include_start,
        ]
        if (len(self._include_exact) > 0) and any([len(attr) > 0 for attr in others]):
            raise ValueError(
                "If `include_exact` is used, do not input any other options."
            )

        if not isinstance(self._include_exact, str):
            raise TypeError("`include_exact` should be a str.")

        if not isinstance(self._include_end, str):
            raise TypeError("`include_end` should be a str.")

        if not isinstance(self._include_start, str):
            raise TypeError("`include_start` should be a str.")

    def exclude(self, string: Union[str, list]):
        """Exclude string from anywhere in matches.

        Parameters
        ----------
        string: str, list
            Matches with regular expression `pattern` will not contain string(s).

        Notes
        -----
        As a list of strings, this acts as a logical "or" for the exclusions.
        """

        if string != "":
            self._exclude += astype(string, list)
        self.check()

    def exclude_start(self, string: Union[str, list]):
        """Exclude string from start of matches.

        Parameters
        ----------
        string: str, list
            Matches with regular expression `pattern` will not start with string(s).

        Notes
        -----
        As a list of strings, this acts as a logical "or" for the exclusions.
        """

        if string != "":
            self._exclude_start += astype(string, list)
        self.check()

    def exclude_end(self, string: Union[str, list]):
        """Exclude string from end of matches.

        Parameters
        ----------
        string: str, list
            Matches with regular expression `pattern` will not end with string(s).

        Notes
        -----
        As a list of strings, this acts as a logical "or" for the exclusions.
        """

        if string != "":
            self._exclude_end += astype(string, list)
        self.check()

    def include_exact(self, string: str):
        """String must match exactly.

        Parameters
        ----------
        string: str
            A match with regular expression `pattern` will be exactly string.
        """

        if len(self._include_exact) > 0:
            raise ValueError("`include_exact` already contains a string.")
        if string != "":
            self._include_exact = string
        self.check()

    def include(self, string: Union[str, list]):
        """String must be present anywhere in matches, logical "and".

        Parameters
        ----------
        string: str, list
            Matches with regular expression `pattern` will contain all string(s).

        Notes
        -----
        A list of strings will be treated as a logical "and".
        """

        if string != "":
            self._include += astype(string, list)
        self.check()

    def include_or(self, string: Union[str, list]):
        """String must be present anywhere in matches, logical "or".

        Parameters
        ----------
        string: str, list
            Matches with regular expression `pattern` will contain at lease one of string(s).

        Notes
        -----
        A list of strings will be treated as a logical "or".
        """

        if string != "":
            self._include += astype(string, list)
        self.check()

    def include_end(self, string: str):
        """String must be present at the end of matches.

        Parameters
        ----------
        string: str
            Matches with regular expression `pattern` will end with string.
        """

        if len(self._include_end) > 0:
            raise ValueError("`include_end` already contains a string.")
        if string != "":
            self._include_end = string
        self.check()

    def include_start(self, string: str):
        """String must be present at the start of matches.

        Parameters
        ----------
        string: str
            Matches with regular expression `pattern` will start with string.
        """

        if len(self._include_start) > 0:
            raise ValueError("`include_start` already contains a string.")
        if string != "":
            self._include_start = string
        self.check()

    def pattern(self) -> str:
        """Generate regular expression pattern from user rules.

        Returns
        -------
        str
            Regular expression accounting for all input selections.
        """

        self._pattern = ""

        # the order of these statements is critical to get expressions correct
        if self.ignore_case:
            self._pattern += "(?i)"

        if len(self._exclude) > 0:  # this should be first
            self._pattern += f"^(?!.*({'|'.join(self._exclude)}))"

        if len(self._exclude_start) > 0:
            self._pattern += f"^(?!({'|'.join(self._exclude_start)}))"

        if len(self._exclude_end) > 0:
            self._pattern += f"(?!.*({'|'.join(self._exclude_end)})$)"

        if len(self._include_start) > 0:
            self._pattern += f"^{self._include_start}.*"

        # this is logical "or"
        if len(self._include_or) > 0:
            self._pattern += f".*({'|'.join(self._include_or)}).*"

        # this is logical "and"
        if len(self._include) > 0:
            self._pattern += "".join([f"(?=.*{string})" for string in self._include])

        if len(self._include_end) > 0:
            self._pattern += f".*{self._include_end}$"

        # Exact matches are their own expression, not combined with any others.
        if len(self._include_exact) > 0:
            self._pattern = f"{self._include_exact}$"

        return self._pattern


def joinpat(regs: Sequence[Reg]) -> str:
    """Join patterns from Reg objects.

    Parameters
    ----------
    regs: Sequence
        Reg objects from which `.pattern()` will be used.

    Returns
    -------
    str
        Regular expression patterns from regs joined together with "|"
    """

    return "|".join([reg.pattern() for reg in regs])
