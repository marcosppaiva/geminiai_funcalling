import pandas as pd
import plotly.express as px
import streamlit as st
import vertexai
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

load_dotenv()
vertexai.init(project="useful-music-410216")

TABLE_NAME = "houses"

engine = create_engine("sqlite:///houses.db")


def get_schema() -> str:
    return """
    Column Name | Type
    price | INTEGER 
    energy_certify | TEXT
    metric | FLOAT
    description | TEXT
    rooms | INTEGER
    company | TEXT
    property_type | TEXT
    district | TEXT
    bathroom | FLOAT
    condition | TEXT
    """


def sql_query(query: str) -> pd.DataFrame:
    """ """
    df = pd.read_sql(
        query,
        con=engine.connect(),
    )
    return df


def list_tables() -> list[str]:
    return [TABLE_NAME]


def plot_graphs(x_axies, y_axies, title):
    return px.scatter(x=x_axies, y=y_axies, title=title)


sql_query_func = FunctionDeclaration(
    name="sql_query",
    description="Get information from data in Sqlite using SQL queries",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query on a single line that will help give quantitative answers to the user's question when run on a Sqlite dataset and table. In the SQL query, always use the fully qualified table names.",
            }
        },
        "required": ["query"],
    },
)

plot_func = FunctionDeclaration(
    name="plot_graphs",
    description="Get information from data in Sqlite using SQL queries and plot a scatterplot",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query on a single line that will help give quantitative answers to the user's question when run on a Sqlite dataset and table. In the SQL query, always use the fully qualified table names.",
            },
        },
        "required": ["query"],
    },
)

get_schema_func = FunctionDeclaration(
    name="get_schema",
    description="Get information about a dataset, including the description, schema, and number of rows that will help answer the user's question. Always use the fully qualified dataset and table names.",
    parameters={"type": "object", "properties": {}},
)

list_tables_func = FunctionDeclaration(
    name="list_tables",
    description="Get a list of tables name that will help answer the user's question",
    parameters={"type": "object", "properties": {}},
)


sql_query_tool = Tool(
    function_declarations=[sql_query_func, get_schema_func, list_tables_func, plot_func]
)


st.set_page_config(
    page_title="Demo Function Calling - Vertex AI", initial_sidebar_state="collapsed"
)


with st.sidebar:
    model_name = st.selectbox(
        "LLm Model:", ("gemini-1.0-pro", "gemini-1.5.pro-preview-0409"), disabled=True
    )

    st.write("Model Parameters:")

    temperature = st.slider(
        "Temperature", min_value=0.0, max_value=1.0, step=0.1, value=0.0
    )
    max_output_tokens = st.slider(
        "Max Output Tokens", min_value=0, max_value=8192, step=1, value=8192
    )


model = GenerativeModel(
    model_name="gemini-1.0-pro",
    generation_config=GenerationConfig(
        temperature=temperature, max_output_tokens=max_output_tokens
    ),
    system_instruction=[
        "You are a helful assistant to help users about houses prices. The table name is houses",
        f"the schema of houses table is {get_schema()}",
    ],
    tools=[sql_query_tool],
)


st.subheader("Function Calling Demo - Gemini \n Developed by: Marcos Paulo")


with st.expander("Some Prompts", expanded=True):
    st.write(
        """
        This demo aims to use function call to help talk to data available in a database
        - What is the most expensive house?
        - plot a scatterplot of house prices by number of bedrooms
        - Give 10 houses where located in Lisboa
        """
    )


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about information in database..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        chat = model.start_chat()  # response_validation=False

        response = chat.send_message(prompt)
        print(f"Full Response: {response}")
        response = response.candidates[0].content.parts[0]  # type: ignore

        print(f"Response: {response}")

        print(f"Function calls: {response.function_call}")

        function_calling_in_process = True
        responses = []
        while function_calling_in_process:
            try:
                params = {}
                for key, value in response.function_call.args.items():  # type: ignore
                    params[key] = value

                function_call_name = response.function_call.name  # type: ignore
                print(f"Function call name: {function_call_name}")
                print(f"Params: {params}")

                if function_call_name == "get_schema":
                    function_response = get_schema()
                    responses.append([function_call_name, params, function_response])
                if function_call_name == "list_tables":
                    function_response = list_tables()
                    responses.append([function_call_name, params, function_response])
                if function_call_name == "sql_query":
                    try:
                        cleaned_query = (
                            params["query"]
                            .replace("\\n", " ")
                            .replace("\n", "")
                            .replace("\\", "")
                            .replace("public.", "")
                        )

                        with engine.connect() as con:
                            function_response = con.execute(
                                text(cleaned_query)
                            ).fetchall()

                        responses.append(
                            [function_call_name, params, function_response]
                        )
                    except Exception as e:
                        print(e)
                        function_response = f"{str(e)}"
                        responses.append(
                            [function_call_name, params, function_response]
                        )

                if function_call_name == "plot_graphs":
                    cleaned_query = (
                        params["query"]
                        .replace("\\n", " ")
                        .replace("\n", "")
                        .replace("\\", "")
                        .replace("public.", "")
                    )

                    with engine.connect() as con:
                        function_response = con.execute(text(cleaned_query)).fetchall()

                    # Preparar os dados para o scatterplot
                    precos = [dado[0] for dado in function_response]
                    quartos = [dado[1] for dado in function_response]

                    function_response = plot_graphs(
                        x_axies=precos,
                        y_axies=quartos,
                        title="Teste",
                    )
                    responses.append([function_call_name, params, function_response])

                    with message_placeholder.container():
                        st.plotly_chart(function_response)

                    function_calling_in_process = False

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": function_response,
                        }
                    )
                    continue

                print(function_response)

                response = chat.send_message(
                    Part.from_function_response(
                        name=function_call_name,
                        response={
                            "content": function_response,
                        },
                    ),
                )
            except AttributeError:
                function_calling_in_process = False

        if (function_call_name != "plot_graphs") and (function_call_name in locals()):
            full_response = response.text  # type: ignore
            with message_placeholder.container():
                st.markdown(full_response.replace("$", "\$"))  # noqa: W605

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                }
            )
