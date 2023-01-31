"""
cf-pandas: an accessor for pandas objects that interprets CF attributes
"""

from importlib.metadata import PackageNotFoundError, version

from .accessor import CFAccessor  # noqa
from .options import set_options  # noqa
from .reg import Reg
from .utils import always_iterable, astype, match_criteria_key, standard_names
from .vocab import Vocab, merge
from .widget import Selector, dropdown

try:
    __version__ = version("cf-pandas")
except PackageNotFoundError:
    # package is not installed
    pass
