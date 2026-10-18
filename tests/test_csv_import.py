import io

import pytest
from app.analysis.csv_import import REQUIRED_COLUMNS, load_gsc_csv
from app.analysis.detectors import detect_ctr_decline
from app.analysis.sample_data import build_sample_data

def test_aliases_commas_and_extra_columns():
    csv = (
        "Date,Top pages,Clicks,Impressions,CTR,Position\n"
        "2026-10-01,/a,5,100,5%,3.2\n"
        '2026-10-02,/a,"1,200","20,000",6%,3.1\n'
    )
    df = load_gsc_csv(io.StringIO(csv))
    assert list(df.columns) == REQUIRED_COLUMNS
    assert df["clicks"].tolist() == [5,1200]


def test_missing_column_raise():
    with pytest.raises(ValueError, match="missing"):
        load_gsc_csv(io.StringIO("Date,Page,Clicks\n2026-10-01,/a,5\n"))

def test_clicks_above_impressions_raises():
    csv = "date,page,clicks,impressions,position\n2026-10-01,/a,50,10,3.0\n"
    with pytest.raises(ValueError, match="greater"):
        load_gsc_csv(io.StringIO(csv))

def test_sample_csv_roundtrip(tmp_path):
    gsc, _ = build_sample_data()
    path = tmp_path / "gsc.csv"
    gsc.to_csv(path, index=False)
    loaded = load_gsc_csv(path)
    pages = {i.page_url for i in detect_ctr_decline(loaded, "example.com")}
    assert "/blog/seo-basics" in pages