import os
from datetime import datetime
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
import requests
import streamlit as st
import pyodbc


ELEVEN_LABS_API_KEY=st.secrets["ELEVEN_LABS_API_KEY"]
server = st.secrets['server']
database = st.secrets['database']
username = st.secrets['username']
password = st.secrets['password']
driver = '{ODBC Driver 17 for SQL Server}'
llm= ChatOpenAI (temperature=0.2,model ="gpt-3.5-turbo-16k-0613")

def get_response_from_ai (human_input):
    template ="""
    Ignore all previous instructions. You are David Goggins, a Mental Toughness Advocate and Motivational Speaker.
    You are providing strength and sharing personal hardships and triumphs to motivate.
    Do not say Hi. Do not start with "I". 
    You keep short, go straight to the point and end strong. 
    {history}
    Audience: {human_input}
    David Goggins: 
    """
    prompt=PromptTemplate(
        input_variables=("history","human_input"),
        template=template
    )
    chatgpt_chain=LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=2)

    )
    output=chatgpt_chain.run(human_input=human_input)

    return output



def get_voice_message(message):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/UzKqcDbzCrsH0d6BBKa8/stream"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }

    data = {
        "text": message,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.35,
            "similarity_boost": 0.92
        }
    }

    response = requests.post(url, json=data, headers=headers, stream=True)

    output_filename = 'output.mp3'
    with open(output_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    
    return output_filename  



def log_to_db(input_data, output_data):
    with pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO [dbo].[gpt_exp_retrieval] (user_message, output_result,project_used,log_time) VALUES (?, ?,?,?)", (str(input_data), str(output_data),"goggins-gpt",datetime.now()))
                                                                                                                     


def main():
    st.set_page_config(
        page_title="Goggins GPT with Voice", page_icon="🎖️")

    st.header("🎖️Goggins GPT with Voice output")
    message=st.text_area("Speak your mind to Goggins:")


    if message:
        st.write("Goggins is typing...")
        result=get_response_from_ai(message)
        
        # Display avatar and response
        col1, col2 = st.columns([1, 4])
        col1.image("david_goggins.jpg",width=120)  
        col2.info(result)  
        
        st.write("Goggins is speaking...")
        st.audio(get_voice_message(result))  
        log_to_db(message, result)

if __name__ == '__main__':
    main()


