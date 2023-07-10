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
    "0x80c67432656d59144ceff962e8faf8926599bcf8",
    "0x80c67432656d59144ceff962e8faf8926599bcf8"
  ]
}
```

**This is a lot more efficient to pass many addresses**