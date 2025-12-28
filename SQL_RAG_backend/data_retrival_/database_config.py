from langchain_community.utilities import SQLDatabase

host = 'localhost'                                                                                                                  
port = '5432'
username = 'postgres'
password = 'root'
database_schema = 'Chatbot'
mysql_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_schema}"


def data_config():
    db = SQLDatabase.from_uri(mysql_uri)
    return db