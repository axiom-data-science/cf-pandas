"""Test cf-pandas utils."""

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


def test_standard_names():

    names = cfp.standard_names()
    assert "sea_water_temperature" in names
