import os
from typing import List, Any

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sbdata.FlipsideApi import FlipsideApi

from src.sql.template import get_sql_template, get_sql_template_with_intermediate_tables

app = FastAPI()


class ArrayInput(BaseModel):
    address_list: List[str] = Field(..., title="Data", description="List of addresses to infer")


class DataFrame(BaseModel):
    columns: List[str]
    index: List[int]
    data: List[List[Any]]


class SqlInput(BaseModel):
    network: str = Field(..., title="Network", description="Network to query")
    sql: str = Field(..., title="SQL", description="SQL query to run")


class JsonInputSql(BaseModel):
    sql_address_list: str = Field(..., title="Address list", description="List of addresses to infer as a sql query")
    network: str = Field(..., title="Network", description="Network to query")
    intermediate_tables: str = Field(..., title="Intermediate tables", description="List of intermediate tables to be "
                                                                                   "used in the query")


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
    result = run_script(input.address_list)
    return {"result": result}


@app.post("/infer/{network}",
          summary="Inference endpoint with a specific network",
          description="it can be any of the following: ethereum, optimism, arbitrum, polygon, bsc, gnosis, fantom, "
                      "avalanche",
          response_description="Inference result")
async def query_data(network: str, input: ArrayInput):
    result = run_script(input.address_list, network)
    return {"result": result}


@app.post("/infer/{network}/sql",
          summary="Inference endpoint with a specific network using a SQL query for the address list",
          description="it can be any of the following: ethereum, optimism, arbitrum, polygon, bsc, gnosis, fantom, "
                      "avalanche. This is the most efficient way to query a large number of addresses",
          response_description="Inference result")
async def query_data(network: str, input: ArrayInput):
    result = run_script(input.address_list, network, sql=True)
    return {"result": result}


@app.post("/inferSql",
          summary="Inference endpoint, all parameters in the query",
          description="it can be any of the following: ethereum, optimism, arbitrum, polygon, bsc, gnosis, fantom, "
                      "avalanche. This is the most efficient way to query a large number of addresses"
                      "intermediate table is the table that contains the addresses to query"
                      "address_list can use tables defined in the intermediate table or a list of addresses",
          response_description="Inference result")
async def query_data(input: JsonInputSql):
    result = run_script(input.sql_address_list, input.network, sql=True, intermediate_tables=input.intermediate_tables)
    return {"result": result}


@app.post("/inferFullSql",
          summary="Inference endpoint, all parameters in the query",
          description="it can be any of the following: ethereum, optimism, arbitrum, polygon, bsc, gnosis, fantom, "
                      "avalanche. This is the most efficient way to query a large number of addresses"
                      "intermediate table is the table that contains the addresses to query"
                      "address_list can use tables defined in the intermediate table or a list of addresses",
          response_description="Inference result")
async def query_data(input: SqlInput):
    print(input.sql)
    print(input.network)
    result = run_script(None, input.network, sql=True, full_sql=input.sql)
    return {"result": result}


def preprocessing(df_features):
    df_features.drop('__row_index', axis=1, inplace=True)
    df_features.set_index('eoa', inplace=True)
    df_features.fillna(0, inplace=True)
    df_features['ratio_tx_counterparties'] = df_features['n_tx'] / df_features['n_counterparty']
    return df_features


def format_prediction(input_array, prediction):
    df_prediction = pd.DataFrame({'eoa': input_array, 'prediction': prediction})
    return df_prediction.to_json(orient='split')


def get_table_name(network):
    if network in ['ethereum', 'optimism', 'arbitrum', 'polygon', 'bsc', 'gnosis', 'fantom', 'avalanche']:
        table_name = f'{network}.core.fact_transactions'
    else:
        raise ValueError(f'Network {network} not supported')
    return table_name


def run_script(input_array, network='ethereum', sql=False, intermediate_tables=None, full_sql=None):
    # Use Flipside to extract features from transactions
    table_name = get_table_name(network)

    flipside_api = FlipsideApi(os.environ.get("FLIPSIDE_API_KEY"), timeout_minutes=10, max_address=1000)

    if sql:
        if full_sql is not None:
            sql_template = full_sql
        else:
            if intermediate_tables is not None:
                sql_template = get_sql_template_with_intermediate_tables(table_name, intermediate_tables, input_array)
            else:
                sql_template = get_sql_template(table_name, input_array)
        df_features = flipside_api.execute_query(sql_template)
    else:
        sql_template = get_sql_template(table_name, '%s')
        df_features = flipside_api.extract_data_flipside(input_array, sql_template)

    df_features = preprocessing(df_features)
    prediction = run_model(df_features, network)
    prediction_json = format_prediction(df_features.index.values, prediction)

    return prediction_json


def run_model(df_features, network='ethereum'):
    model_name = f'{network}_cex_dex_logistic_best.joblib'
    # Use our model to predict the label
    model = joblib.load(os.path.join('model', model_name))
    prediction = model.predict(df_features)

    return prediction
