"""
cf-pandas: an accessor for pandas objects that interprets CF attributes
"""

from pkg_resources import DistributionNotFound, get_distribution


try:
    __version__ = get_distribution("cf-pandas").version
except DistributionNotFound:
    # package is not installed
    __version__ = "unknown"
