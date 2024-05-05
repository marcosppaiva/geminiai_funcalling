# %%
import os

import requests
import vertexai
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

# %%
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    "/Users/marcospaulopaivapereira/Documents/Projetos/llm_funcalling/.keys/credentials.json"
)

vertexai.init(project="useful-music-410216")

# %%
get_product_info = FunctionDeclaration(
    name="get_product_info",
    description="Get the stock amount and identifier for a given product",
    parameters={
        "type": "object",
        "properties": {
            "product_name": {"type": "string", "description": "Product name"}
        },
    },
)


get_products = FunctionDeclaration(
    name="get_products",
    description="Get a list of products that are registered",
    parameters={"type": "object", "properties": {}},
)

# %%
retail_tools = Tool(function_declarations=[get_product_info, get_products])
# %%
model = GenerativeModel(
    model_name="gemini-1.0-pro",
    generation_config=GenerationConfig(temperature=0),
    tools=[retail_tools],
)
# %%
chat = model.start_chat()

# %%
prompt = """Do you have the Galaxy S24 Ultra in stock?"""
prompt_2 = """What products do you have?"""
# %%
response = chat.send_message(prompt_2)
print(f"First response {response}")

# %%
print(response.candidates[0].content.parts[0].function_call)


# %%
params = {}
for key, value in response.candidates[0].content.parts[0].function_call.args.items():
    print(f"Key is: {key} and value is {value}")
    params[key] = value

# %%
if response.candidates[0].content.parts[0].function_call.name == "get_product_info":
    content = requests.get(f"http://127.0.0.1:8000/products/{params['product_name']}")
if response.candidates[0].content.parts[0].function_call.name == "get_products":
    content = requests.get(f"http://127.0.0.1:8000/products/")

# %%
print(content.text)

# %%
if content.status_code == 200:
    api_response = content.text

    response = chat.send_message(
        Part.from_function_response(
            name=response.candidates[0].content.parts[0].function_call.name,
            response={"content": api_response},
        )
    )

print(response)

# %%
import pandas as pd

df = pd.read_parquet("../data/data.parquet")
display(df.head())

# %%
from sqlalchemy import create_engine

engine = create_engine("sqlite:///houses.db")

df.to_sql("houses", con=engine.connect(), index=False, if_exists="replace")
# %%
cursor = engine.raw_connection().cursor()
cursor.execute(
    "select sql from sqlite_master where type = 'table' and name = 'houses';"
)
print(cursor.fetchall())
cursor.close()

# %%
cursor = engine.raw_connection().cursor()
cursor.execute("PRAGMA table_info('houses')")

print(cursor.fetchall())
cursor.close()
# %%
