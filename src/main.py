from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()


class ArrayInput(BaseModel):
    data: List[int]  # or another appropriate type


@app.post("/query")
async def query_data(input: ArrayInput):
    result = run_script(input.data)
    return {"result": result}


def run_script(input_array):
    result = input_array
    return result
