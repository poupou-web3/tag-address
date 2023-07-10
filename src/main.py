import json
import os
from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from sbdata.FlipsideApi import FlipsideApi

from src.sql.template import sql_template

app = FastAPI()

root_path = Path.cwd().parent


class ArrayInput(BaseModel):
    data: List[str]


@app.post("/query")
async def query_data(input: ArrayInput):
    result = run_script(input.data)
    return {"result": result}


def preprocessing(df_features):
    df_features['ratio_tx_counterparties'] = df_features['n_tx'] / df_features['n_counterparty']
    return df_features


def format_prediction(input_array, prediction):
    df_prediction = pd.DataFrame({'eoa': input_array, 'prediction': prediction})
    return df_prediction.to_json(orient='split')


def run_script(input_array):
    # Use Flipside to extract features from transactions
    flipside_api = FlipsideApi(os.environ.get("FLIPSIDE_API_KEY2"), timeout_minutes=10, max_address=1000)
    df_features = flipside_api.extract_data_flipside(input_array, sql_template)
    df_features.drop('__row_index', axis=1, inplace=True)
    df_features.set_index('eoa', inplace=True)
    df_features.fillna(0, inplace=True)

    df_features = preprocessing(df_features)
    prediction = run_model(df_features)

    prediction_json = format_prediction(input_array, prediction)
    return prediction_json


def run_model(df_features):
    # Use our model to predict the label
    model = joblib.load(os.path.join(root_path, 'model', 'optimism_cex_dex_logistic_best.joblib'))
    prediction = model.predict(df_features)

    return prediction
