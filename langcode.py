from langchain_google_genai import GoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
import pymysql
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool, InfoSQLDatabaseTool, ListSQLDatabaseTool, QuerySQLCheckerTool
from langchain_core.prompts import (ChatPromptTemplate, FewShotPromptTemplate, PromptTemplate)
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
import os
import keyval



os.environ["GOOGLE_API_KEY"] = keyval.GOOGLE_API_KEY

def get_response():


    llm = GoogleGenerativeAI(model="gemini-pro",temperature=0)


    db_user = "root"
    db_password = "YOUR_PASSWORD"
    db_host = "YOUR_HOST"
    db_name = "DATABASE_NAME"
    db = SQLDatabase.from_uri(
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=3)
    # print(db.table_info)




    examples=[ {'input' : "How many t-shirts do we have left for Nike in XS size and white color?",
         'query' : "SELECT sum(stock_quantity) FROM t_shirts WHERE brand = 'Nike' AND color = 'White' AND size = 'XS'"
         },
        {'input': "How much is the total price of the inventory for all S-size t-shirts?",
         'query':"SELECT SUM(price*stock_quantity) FROM t_shirts WHERE size = 'S'"
         },
        {'input': "If we have to sell all the Levi’s T-shirts today with discounts applied. How much revenue  our store will generate (post discounts)?" ,
         'query' : """SELECT sum(a.total_amount * ((100-COALESCE(discounts.pct_discount,0))/100)) as total_revenue from
    (select sum(price*stock_quantity) as total_amount, t_shirt_id from t_shirts where brand = 'Levi'
    group by t_shirt_id) a left join discounts on a.t_shirt_id = discounts.t_shirt_id
     """
         } ,
         {'input' : "If we have to sell all the Levi’s T-shirts today. How much revenue our store will generate without discount?" ,
          'query': "SELECT SUM(price * stock_quantity) FROM t_shirts WHERE brand = 'Levi'"
          },
        {'input': "How many white color Levi's shirt I have?",
         'query' : "SELECT sum(stock_quantity) FROM t_shirts WHERE brand = 'Levi' AND color = 'White'"

         },
        {'input': "how much sales amount will be generated if we sell all large size t shirts today in nike brand after discounts?",
         'query' : """SELECT sum(a.total_amount * ((100-COALESCE(discounts.pct_discount,0))/100)) as total_revenue from
    (select sum(price*stock_quantity) as total_amount, t_shirt_id from t_shirts where brand = 'Nike' and size="L"
    group by t_shirt_id) a left join discounts on a.t_shirt_id = discounts.t_shirt_id
     """}
         ]

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        embeddings,
        Chroma,
        k=3,
        input_keys=["input"],
        )


    sql_db_query =  QuerySQLDataBaseTool(db = db)
    sql_db_schema =  InfoSQLDatabaseTool(db = db)
    sql_db_list_tables =  ListSQLDatabaseTool(db = db)
    sql_db_query_checker = QuerySQLCheckerTool(db = db, llm = llm)

    tools = [sql_db_query, sql_db_schema, sql_db_list_tables, sql_db_query_checker]


    system_prefix = """
    Answer the following questions as best you can. You have access to the following tools:
    
    {tools}
    
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Here are some examples of user inputs and their corresponding SQL queries:
    
    """

    suffix = """
    Begin!
    
    Question: {input}
    Thought:{agent_scratchpad}
    """

    dynamic_few_shot_prompt_template = FewShotPromptTemplate(
        example_selector = example_selector,
        example_prompt=PromptTemplate.from_template(
            "User input: {input}\nSQL query: {query}"
        ),
        input_variables=["input"],
        prefix=system_prefix,
        suffix=suffix
    )

    full_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate(prompt=dynamic_few_shot_prompt_template),
        ]
    )

    agent = create_react_agent(llm, tools, full_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


    return agent_executor





