import pandas as pd
import numpy as np
import pytest 

from src.survival import collapse_to_occurrences, assign_censoring

def test_collapse_to_occurrences():
    df = pd.DataFrame({
        "user_id" : [1, 2, 2, 3, 3],
        "user_session" : ["111", "222", "222", "333", "333"],
        "event_time" : pd.to_datetime(["2019-11-25 03:07:56", "2019-11-25 05:07:13", "2019-11-25 05:07:13", "2019-11-27 02:10:13", "2019-11-30 06:07:01"]),
        "is_refund" : [1, 0, 0, 0, 0]
    })

    expected_result = pd.DataFrame({
        "user_id" : [1, 2, 3],
        "user_session" : ["111", "222", "333"],
        "occasion_time" : pd.to_datetime(["2019-11-25 03:07:56", "2019-11-25 05:07:13", "2019-11-27 02:10:13"]),
        "has_refund" : [1, 0, 0],
        "n_items" : [1, 2, 2]
    })

    result = collapse_to_occurrences(df)
    assert result["user_id"].to_list() == expected_result["user_id"].to_list()
    assert result["user_session"].to_list() == expected_result["user_session"].to_list()
    assert result["occasion_time"].to_list() == expected_result["occasion_time"].to_list()
    assert result["has_refund"].to_list() == expected_result["has_refund"].to_list()


def test_assign_censoring_properly_labels():
    df = pd.DataFrame({
            "user_id" : [1, 1, 2],
            "user_session" : ["111", "222", "333"],
            "occasion_time" : pd.to_datetime(["2019-11-25 03:00", "2019-11-26 03:00", "2019-11-27 02:00"]),
            "has_refund" : [1, 0, 0],
            "n_items" : [1, 2, 2]
        })
    
    dataset_end = pd.to_datetime("2019 11-30 03:00")
    result = assign_censoring(df, dataset_end)


    
    assert result["next_occasion_time"].to_list() == [pd.to_datetime("2019 11-26 03:00"), pd.NaT, pd.NaT]
    assert result["censored"].to_list() == [0, 1, 1]
    assert result["duration_days"].to_list() == [1.0, 4.0, 3.0416666666666665] 


     