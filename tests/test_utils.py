"""Test cf-pandas utils."""

from unittest import mock

import requests

import cf_pandas as cfp

criteria = {
    "wind_s": {
        "standard_name": "wind_speed$",
    },
}


def test_match_criteria_key():

    vals = ["wind_speed", "WIND_SPEED", "wind_speed_status"]

    # test function with set_options criteria
    with cfp.set_options(custom_criteria=criteria):
        assert cfp.match_criteria_key(vals, ["wind_s"]) == ["wind_speed"]

    # test function with input criteria
    assert cfp.match_criteria_key(vals, ["wind_s"], criteria) == ["wind_speed"]


def test_match_criteria_key_split():

    vals = ["wind_speed (m/s)", "WIND_SPEED", "wind_speed_status"]

    # test function with set_options criteria
    with cfp.set_options(custom_criteria=criteria):
        assert cfp.match_criteria_key(vals, ["wind_s"], split=True) == [
            "wind_speed (m/s)"
        ]

    # test function with input criteria
    assert cfp.match_criteria_key(vals, ["wind_s"], criteria, split=True) == [
        "wind_speed (m/s)"
    ]


@mock.patch("requests.get")
def test_standard_names(mock_requests):

    resp = requests.models.Response
    resp.content = b"""<?xml version="1.0"?>\n<standard_name_table xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="cf-standard-name-table-1.1.xsd">\n   <version_number>79</version_number>\n   <last_modified>2022-03-19T15:25:54Z</last_modified>\n   <institution>Centre for Environmental Data Analysis</institution>\n   <contact>support@ceda.ac.uk</contact>\n\n  \n   <entry id="longitude">\n      </entry>\n  \n   <entry id="wind_speed">\n  """
    mock_requests.return_value = resp
    names = cfp.standard_names()
    assert "wind_speed" in names
