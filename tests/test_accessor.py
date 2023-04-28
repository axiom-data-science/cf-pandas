"""Test cf-pandas."""

from unittest import mock

import numpy as np
import pandas as pd
import pytest
import requests

import cf_pandas as cfp

criteria = {
    "wind_s": {
        "standard_name": "wind_speed$",
    },
    "temp2": {
        "standard_name": "temp$",
    },
    "salt2": {"standard_name": "sal$"},
}


def test_options():
    # test for inputting a nonexistent option
    with pytest.raises(ValueError):
        cfp.set_options(DISPLAY_WIDTH=80)


def test_validate():
    df = pd.DataFrame(
        columns=[
            "temp",
        ]
    )
    with pytest.raises(AttributeError):
        df.cf._validate()


def test_match_criteria_key_accessor():

    df = pd.DataFrame(
        columns=[
            "temp",
            "wind_speed",
            "wind_speed (m/s)",
            "WIND_SPEED",
            "wind_speed_status",
            "longitude (degrees_east)",
            "X",
            "latitude",
            "time",
        ]
    )

    # test accessor with set_options criteria
    with cfp.set_options(custom_criteria=criteria):
        assert sorted(df.cf["wind_s"].columns) == ["wind_speed", "wind_speed (m/s)"]
        assert isinstance(df.cf["wind_s"], pd.DataFrame)
        assert df.cf["temp2"].name == "temp"
        assert isinstance(df.cf["temp2"], pd.Series)
        assert df.cf["longitude"].name == "longitude (degrees_east)"
        assert df.cf.custom_keys["temp2"] == ["temp"]
        assert sorted(df.cf.custom_keys["wind_s"]) == ["wind_speed", "wind_speed (m/s)"]
        assert sorted(df.cf.axes) == ["T", "X"]
        assert sorted(df.cf.coordinates) == ["latitude", "longitude", "time"]
        assert sorted(df.cf.keys()) == [
            "T",
            "X",
            "latitude",
            "longitude",
            "temp2",
            "time",
            "wind_s",
        ]
        assert "X" in df.cf
        assert "Y" not in df.cf
        assert "salt2" not in df.cf


@mock.patch("requests.get")
def test_standard_names(mock_requests):

    resp = requests.models.Response
    resp.content = b"""<?xml version="1.0"?>\n<standard_name_table xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="cf-standard-name-table-1.1.xsd">\n   <version_number>79</version_number>\n   <last_modified>2022-03-19T15:25:54Z</last_modified>\n   <institution>Centre for Environmental Data Analysis</institution>\n   <contact>support@ceda.ac.uk</contact>\n\n  \n   <entry id="longitude">\n      </entry>\n  \n   <entry id="wind_speed">\n  """
    mock_requests.return_value = resp
    df = pd.DataFrame(
        columns=[
            "temp",
            "wind_speed",
            "wind_speed (m/s)",
            "WIND_SPEED",
            "wind_speed_status",
            "longitude (degrees_east)",
            "X",
            "latitude",
            "time",
        ]
    )
    assert df.cf.standard_names["longitude"] == ["longitude (degrees_east)"]
    assert sorted(df.cf.standard_names["wind_speed"]) == [
        "wind_speed",
        "wind_speed (m/s)",
    ]


def test_set_item():
    df = pd.DataFrame(
        columns=[
            "temp",
            "wind_speed",
            "wind_speed (m/s)",
            "WIND_SPEED",
            "wind_speed_status",
            "longitude",
            "latitude",
            "time",
        ]
    )
    with cfp.set_options(custom_criteria=criteria):
        df.cf["temp"] = np.arange(8)
        assert all(df.cf["temp"].values == np.arange(8))
        df.cf["longitude"] = np.arange(8)
        assert all(df.cf["longitude"].values == np.arange(8))


def test_get_by_guess_regex():
    df = pd.DataFrame(columns=["lon", "lat", "min"])
    assert df.cf["longitude"].name == "lon"
    assert df.cf["latitude"].name == "lat"
    assert df.cf["time"].name == "min"

    df = pd.DataFrame(columns=["blah_lon", "table_lat"])
    assert df.cf["longitude"].name == "blah_lon"
    assert df.cf["latitude"].name == "table_lat"


def test_index():
    """Test when time is in index."""
    df = pd.DataFrame(index=["m_time"])
    df.index.rename("m_time", inplace=True)
    assert df.cf["T"].name == "m_time"


def test_cols():
    df = pd.DataFrame(columns=["m_time", "lon", "lat", "temp"])
    assert df.cf.axes_cols == ["m_time"]
    assert sorted(df.cf.coordinates_cols) == ["lat", "lon", "m_time"]
