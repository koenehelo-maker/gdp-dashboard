"""Smoke tests that run streamlit_app.py headlessly with Streamlit's AppTest."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "streamlit_app.py")


def run_app():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_render():
    at = run_app()
    assert at.header[0].value.startswith("GDP over time")
    # One metric per default country (DEU, FRA, GBR, BRA, MEX, JPN).
    assert len(at.metric) == 6


def test_narrow_year_range_and_one_country():
    at = run_app()
    at.slider[0].set_value((2000, 2010)).run()
    at.multiselect[0].set_value(["ZAF"]).run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.header[1].value.startswith("GDP in 2010")
    assert [m.label for m in at.metric] == ["ZAF GDP"]
