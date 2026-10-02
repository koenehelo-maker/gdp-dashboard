from streamlit.testing.v1 import AppTest

APP = "../streamlit_app.py"
TIMEOUT = 30


def test_default_view_renders():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()

    assert not at.exception
    assert at.slider[0].value == (1960, 2022)
    assert at.multiselect[0].value == ["DEU", "FRA", "GBR", "BRA", "MEX", "JPN"]
    assert len(at.metric) == 6


def test_narrowed_year_range_renders():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT).run()
    at.slider[0].set_value((2000, 2010)).run()

    assert not at.exception
    assert at.header[1].value == "GDP in 2010"
    assert len(at.metric) == 6
