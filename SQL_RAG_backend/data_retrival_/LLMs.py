from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
import os

def ollama3_2_3bmodel():
    llm = ChatOllama(
        model = 'llama3.2:3b',
        temperature= 0.3,
        num_predict= 2048
    )
    return llm

def ollamaph3_mini():
    llm = ChatOllama(
        model = 'phi3:mini',
        temperature= 0.3,
        num_predict= 2048
    )
    return llm

def grokllm():
    llm = ChatGroq(
       model = 'llama-3.3-70b-versatile',
       temperature= 0.3,
       max_tokens=2048,
       api_key = os.getenv("GROQ_API_KEY")
    )
    return llm