from datetime import date
from math import expm1, log1p

import numpy as np
from sklearn.linear_model import LinearRegression


def gap(newer,older):
    return (date.fromisoformat(newer)-date.fromisoformat(older)).days


def features(previous_count,gap_days):
    return [log1p(previous_count),log1p(gap_days)]


def calculate(data):
    observations = sorted(data['observations'],key=lambda row: (row['visit_day'],row['code']))
    rows = [
        (features(past['activity_count'],gap(current['visit_day'],past['visit_day'])),
            log1p(current['activity_count']))
        for past,current in zip(observations,observations[1:])
    ]
    hold = max(3,len(rows)//5)
    train = rows[:-hold]
    model = LinearRegression().fit([x for x,_ in train],[y for _,y in train])
    validation_x = [x for x,_ in rows[-hold:]]
    actual = np.expm1([y for _,y in rows[-hold:]])
    estimates = np.maximum(0,np.expm1(np.clip(model.predict(validation_x),0,9)))
    mae = float(np.mean(np.abs(actual-estimates)))
    model.fit([x for x,_ in rows],[y for _,y in rows])
    newest = observations[-1]
    lag_count = newest['activity_count']
    gap_days = gap(data['target_day'],newest['visit_day'])
    prediction = max(0.,expm1(float(np.clip(model.predict([features(lag_count,gap_days)])[0],0,9))))
    return {'prediction':round(prediction,5),'gap_days':gap_days,'lag_count':lag_count,
        'holdout_mae':round(mae,6),'training_rows':len(train),'holdout_rows':hold,
        'skipped_refusals':data['skipped_refusals'],'observed_zeroes':sum(row['activity_count']==0 for row in observations),
        'validation_from':observations[-hold]['visit_day'],
        'coefficient_prev_count':round(float(model.coef_[0]),6),
        'coefficient_gap_days':round(float(model.coef_[1]),6)}
