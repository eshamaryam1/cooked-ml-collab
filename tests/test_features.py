import pandas as pd

from cooked_ml.features import drop_duplicate_rows


def test_drop_duplicate_rows_removes_exact_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
    out = drop_duplicate_rows(df)
    assert len(out) == 2
    assert out.iloc[0].to_dict() == {"a": 1, "b": 3}


def test_drop_duplicate_rows_keeps_input_unchanged():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
    before = df.copy()
    drop_duplicate_rows(df)
    pd.testing.assert_frame_equal(df, before)


def test_drop_duplicate_rows_resets_index():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
    out = drop_duplicate_rows(df)
    assert list(out.index) == [0, 1]


def test_drop_duplicate_rows_honours_subset():
    df = pd.DataFrame({"a": [1, 1], "b": [3, 4]})
    assert len(drop_duplicate_rows(df, subset=["a"])) == 1
    assert len(drop_duplicate_rows(df)) == 2
