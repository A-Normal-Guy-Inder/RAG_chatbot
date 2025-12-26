from flask import Flask
from flask_restful import Api, Resource, reqparse

from query_retrival_.search import ask_question
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

        return {
            "question": question,
            "response": response
        }, 200

api.add_resource(Chat, "/chat")

if __name__ == "__main__":
    app.run(debug=True)