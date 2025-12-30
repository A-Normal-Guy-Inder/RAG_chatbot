from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits import create_sql_agent
from ..database_config import data_config
from .LLMs import ollama3_2_3bmodel, grokllm, ollamaph3_mini
from .graphTools import GraphGenerator,GraphExplainer
from dotenv import load_dotenv
load_dotenv()

def data_retriever(question : str):
    db=data_config()
    model=grokllm()

    toolkit = SQLDatabaseToolkit(db=db, llm=model)

    agentdb = create_sql_agent(
        llm=model,
        toolkit=toolkit,
        verbose=True
    )

    sqlAnswer= agentdb.invoke(question)

    visualizer = GraphGenerator(model)
    graphtext = visualizer.generate_graph(sqlAnswer)
    if not graphtext:
        return (None,None)
    
    explain = GraphExplainer(model)
    explain_text = explain.strip_plotting_lines(sqlAnswer['output'])

    return (explain.generate_explanation(explain_text),visualizer.generate_plot_base64(graphtext))