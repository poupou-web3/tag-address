# tag-address
This repo expose an api end point that runs a model to tag a crypto address


## How to run the project on windows

### Prerequisites

#### Clone, create a virtual environment and install the requirements

```bash
git clone 
cd tag-address
Python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### launch the api
```bash
uvicorn main:app --reload
```

### You should have a FLIPSIDE_API_KEY in your environment variables

for that create a variable `FLISIDE_API_KEY` with your api key as value

## Test the api in your browser

Go to http://127.0.0.1:8000/docs#/default/query_data_query_post

Edit the post data and replace `string` with the address you want to tag

```json
{
  "data": [
    "string"
  ]
}
```

for example:

```json
{
  "data": [
    "0x80c67432656d59144ceff962e8faf8926599bcf8"
  ]
}
```

You can pass multiple addresses in the array like this:

```json
{
  "data": [
    "0xb9726225b711f5ffe1eb3e117e9caaa0f78dcd37",
    "0x80c67432656d59144ceff962e8faf8926599bcf8"
  ]
}
```

## Python example

```python
import requests
import pandas as pd

array_list = ["0xb9726225b711f5ffe1eb3e117e9caaa0f78dcd37", "0x80c67432656d59144ceff962e8faf8926599bcf8"]

url = "http://127.0.0.1:8000/query"
response = requests.post(url, json={"data": array_list})
df_prediction = pd.read_json(response.json()['result'], orient='split')
print(df_prediction)
```

response = requests.post("http://127.0.0.1:8000/query", json={"data": array_list})

**This is a lot more efficient to pass many addresses**

## Install with docker

### 1. Start docker

### 2. Build the image

```bash
docker build -t tag_address_api .
```

### 3. Run the image

```bash
docker run -e "FLIPSIDE_API_KEY=replace_with_api_key" -p 8000:80 tag_address_api
```

### 4. Test the api in your browser

http://localhost:8000/docs#/default/query_data_query_post

docker run -e "FLIPSIDE_API_KEY=c1180eca-2d3b-451e-adb7-c93e842c4017" -p 8000:80 tag_address_api