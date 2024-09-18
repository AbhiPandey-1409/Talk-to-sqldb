Talk-to-sqldb
This is an end to end LLM project based on Google gemini model and Langchain agents(create_react_agent). We are building a system that can talk to MySQL database. User asks questions in a natural language and the system generates answers by converting those questions to an SQL query and then executing that query on MySQL database. Premium Tshirts is a T-shirt store where they maintain their inventory, sales and discounts data in MySQL database. A store manager will may ask questions such as,

* How many  white color tshirts of nike brand  and size L are there in stock?
* How much sales our store will generate if we can sell all extra-small size t shirts after applying discounts?

The system is intelligent enough to generate accurate queries for given question and execute them on MySQL database as it has been provided with dynamic few shot examples to guide the model how to create queries for that specific input.
The agent used has been given a superspecific prompt that it will follow to answer correctley after multiple loops of thought-action-input-observation-thought again and again untill it gets the final answer.
Streamlit has been used to make things display in a  user interactive interface.
