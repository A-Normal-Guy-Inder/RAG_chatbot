from flask import Flask
from flask_restful import Api, Resource, reqparse

from data_retrival_.search import ask_question
from data_retrival_.sql_retrival import data_retriever
from flask_cors import CORS


app = Flask(__name__)
api = Api(app)
CORS(app)

parser = reqparse.RequestParser()
parser.add_argument(
    "question",
    type=str,
    required=True,
    help="Question is required"
)

class Chat(Resource):
    def post(self):
        args = parser.parse_args()
        question = args["question"]

        response = ask_question(question)
        graph_summary,graph_img = data_retriever(question)
        return {
            "question": question,
            "response": response,
            "graph_summary": graph_summary,
            "graph_img": graph_img
        }, 200

api.add_resource(Chat, "/chat")

if __name__ == "__main__":
    app.run(debug=True)