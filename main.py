import os
from typing import List, Any, Tuple

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sbdata.FlipsideApi import FlipsideApi

from src.sql.template import get_sql_template

app = FastAPI()


class ArrayInput(BaseModel):
    data: List[str] = Field(..., title="Data", description="List of addresses to infer")


class DataFrame(BaseModel):
    columns: List[str]
    index: List[int]
    data: List[List[Any]]


class InferenceResultNetwork(BaseModel):
    result: DataFrame


@app.get("/", include_in_schema=False)
def read_root():
    return {"Welcome to the tagger API, please use the /docs to see the documentation"}


@app.post("/infer",
          summary="Inference endpoint",
          description="By default return the inference on ethereum network",
          response_description="Inference result")
async def query_data(input: ArrayInput):
    result = run_script(input.data)
    return {"result": result}


@app.post("/infer/{network}",
          summary="Inference endpoint with a specific network",
          description="it can be any of the following: ethereum, optimism, arbitrum, polygon, bsc, gnosis, fantom, "
                      "avalanche",
          response_description="Inference result")
async def query_data(network: str, input: ArrayInput):
    result = run_script(input.data, network)
    return {"result": result}


def preprocessing(df_features):
    df_features['ratio_tx_counterparties'] = df_features['n_tx'] / df_features['n_counterparty']
    return df_features


def format_prediction(input_array, prediction):
    df_prediction = pd.DataFrame({'eoa': input_array, 'prediction': prediction})
    return df_prediction.to_json(orient='split')


def run_script(input_array, network='ethereum'):
    # Use Flipside to extract features from transactions
    if network in ['ethereum', 'optimism', 'arbitrum', 'polygon', 'bsc', 'gnosis', 'fantom', 'avalanche']:
        table_name = f'{network}.core.fact_transactions'
    else:
        raise ValueError(f'Network {network} not supported')

    flipside_api = FlipsideApi(os.environ.get("FLIPSIDE_API_KEY"), timeout_minutes=10, max_address=1000)
    sql_template = get_sql_template(table_name, '%s')
    df_features = flipside_api.extract_data_flipside(input_array, sql_template)
    df_features.drop('__row_index', axis=1, inplace=True)
    df_features.set_index('eoa', inplace=True)
    df_features.fillna(0, inplace=True)

    df_features = preprocessing(df_features)
    prediction = run_model(df_features, network)

    prediction_json = format_prediction(input_array, prediction)
    return prediction_json


def run_model(df_features, network='ethereum'):
    model_name = f'{network}_cex_dex_logistic_best.joblib'
    # Use our model to predict the label
    model = joblib.load(os.path.join('model', model_name))
    prediction = model.predict(df_features)

    return prediction
