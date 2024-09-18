import streamlit as st
from langcode import get_response

st.title('Premium Tshirts 👨‍👩‍👧‍👦')
st.header('Ask your question:')
question=st.text_input('Enter your Question here')
Button=st.button('find')

if Button:
    agent_executor= get_response()
    response= agent_executor.invoke({'input':question})
    st.write(response['output'])
