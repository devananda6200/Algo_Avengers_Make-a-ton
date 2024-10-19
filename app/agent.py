from langchain_community.vectorstores import Qdrant
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_together import ChatTogether
from langchain.chains import RetrievalQA
from qdrant_client import QdrantClient
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from config import Config
import json
from typing import Dict, List, Annotated, Any
import json
from langchain.schema import BaseMessage
from langgraph.graph import Graph
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool

embeddings = FastEmbedEmbeddings()
url = Config.QDRANT_URL
api_key = Config.QDRANT_API_KEY

client = QdrantClient(url=url, api_key = api_key)

# Initialize Qdrant as a vector store
vector_store = Qdrant(
    client=client,
    collection_name="test_rag",
    embeddings=embeddings,
)

# Initialize Together AI LLM
llm = ChatTogether(
    together_api_key=Config.TOGETHER_API,
    model="meta-llama/Llama-3-70b-chat-hf",
)
# Create a retriever from the vector store
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
# Define input and state types
class InputType(TypedDict):
    input: str
    num_questions: int

class StateType(TypedDict):
    input: str
    num_questions: int
    rag_result: str
    mcq_json: str

# Define RAG node
def rag_node(state: StateType):
    template = """
    You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know.
    Question: {input}
    Context: {context}
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    result = retrieval_chain.invoke({"input": state["input"]})
    state["rag_result"] = result['answer']
    return state

# Define MCQ generation node
def mcq_generation_node(state: StateType):
    mcq_prompt = f"""
    Based on the following content, generate {state['num_questions']} multiple-choice questions (MCQs).
    Present the questions in JSON format with the following structure:
    {{
        "module": "Topic of the questions",
        "questions": [
            {{
                "question": "Question text",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Correct option"
            }},
            ...
        ]
    }}
    
    Content: {state['rag_result']}
    """
    mcq_result = llm.invoke(mcq_prompt)
    state["mcq_json"] = mcq_result
    return state

# Define the graph
def define_graph():
    workflow = Graph()

    workflow.add_node("RAG", rag_node)
    workflow.add_node("MCQ_Generation", mcq_generation_node)

    workflow.set_entry_point("RAG")
    workflow.add_edge("RAG", "MCQ_Generation")
    workflow.add_edge("MCQ_Generation", END)

    return workflow

# Create the graph
graph = define_graph()

# Compile the graph
app = graph.compile()

# Function to run the graph
def run_graph(input_text: str, num_questions: int):
    input_data: InputType = {"input": input_text, "num_questions": num_questions}
    result = app.invoke(input_data)
    return result

# Example usage
if __name__ == "__main__":
    user_input = "Explain the process of photosynthesis"
    num_questions = 3
    result = run_graph(user_input, num_questions)
    print("RAG Result:", result["rag_result"])
    print("MCQ JSON:", result["mcq_json"])