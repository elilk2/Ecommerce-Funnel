import pandas as pd
import numpy as np

def collapse_to_occurrences(df : pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    occasions = (
       df.groupby(
            ['user_session', 'user_id']
       ).agg(
           occasion_time = ('event_time', 'min'),
           has_refund = ('is_refund', 'max'),
           n_items = ('event_time', 'size')
       )
       .reset_index()
    )

    return occasions

def assign_censoring(occasions : pd.DataFrame, dataset_end : pd.Timestamp) -> pd.DataFrame:

    occasions = occasions.copy()
    occasions = occasions.sort_values(['user_id', 'occasion_time'])
    occasions['next_occasion_time'] = (
        occasions.groupby('user_id')['occasion_time'].shift(-1)
    )

    occasions['days_to_next_purchase'] = (
        occasions['next_occasion_time'] - occasions['occasion_time']
    ).dt.total_seconds() / 86400

    occasions['censored'] = occasions['next_occasion_time'].isna().astype(int)

    occasions['duration_days'] = np.where(
        occasions['censored'] == 1,
        (dataset_end - occasions['occasion_time']).dt.total_seconds() / 86400,
        occasions['days_to_next_purchase'],
    )

    return occasions