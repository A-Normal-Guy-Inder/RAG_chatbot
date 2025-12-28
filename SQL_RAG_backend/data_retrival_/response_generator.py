from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

class ResponseGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a knowledgeable and honest AI assistant.\n\n"
                "Use the information provided in the context to answer the question.\n"
                "Donot say that you are answering by using the context.\n"
                "If the context does not contain sufficient information, say:\n"
                "\"I don't have enough information from the provided sources to answer this question.\"\n\n"
                "Context:\n"
                "{context}\n\n"
                "Question:\n"
                "{question}\n\n"
                "Answer:"
            ),
        )

    def generate_response(self, query: str, context: str, max_chars: int = 4000) -> str:
        if not context or not context.strip():
            return "I don't have enough information from the provided sources to answer this question."

        # Defensive trim
        context = context[:max_chars]

        prompt = self.prompt_template.format(
            context=context,
            question=query
        )

        try:
            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
