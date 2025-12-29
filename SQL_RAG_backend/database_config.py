from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
load_dotenv()
import os

username = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database_schema = os.getenv("DB_NAME")
mysql_url = (f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database_schema}")


def getSqlUrl():
    return mysql_url

def data_config():
    db = SQLDatabase.from_uri(mysql_url)
    return db