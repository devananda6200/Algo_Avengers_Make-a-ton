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
template = """

You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \


Question: {input}
Context: {context}

Answer:

"""

from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StdOutCallbackHandler

prompt = ChatPromptTemplate.from_template(template)
handler =  StdOutCallbackHandler()

combine_docs_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

# Define MCQ generation function
@tool
def generate_mcq(content: str, num_questions: int) -> str:
    """Generate MCQ questions based on the given content."""
    prompt = f"""
    Based on the following content, generate {num_questions} multiple-choice questions (MCQs).
    Format the output as a JSON array with each question having the following structure:
    {{
        "module": "Topic of the question",
        "question": "The question text",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "The correct option"
    }}

    Content: {content}
    """
    response = llm.invoke(prompt)
    return response
# Define the state type
State = Dict[str, Any]

# Define graph nodes
def rag_node(state: State) -> State:
    result = retrieval_chain.invoke({"input": state['user_input']})
    state['rag_output'] = result['answer']
    return state

def mcq_node(state: State) -> State:
    mcq_json = generate_mcq(state['rag_output'], state['num_questions'])
    state['mcq_json'] = mcq_json
    return state

# Define the graph
workflow = Graph()

# Add nodes to the graph
workflow.add_node("RAG", rag_node)
workflow.add_node("MCQ_Generator", mcq_node)

# Connect the nodes
workflow.add_edge('RAG', 'MCQ_Generator')

# Set the entry point
workflow.set_entry_point("RAG")

# Compile the graph
app = workflow.compile()

# Function to run the graph
def run_graph(user_input: str, num_questions: int):
    inputs = {
    "user_input": user_input,
    "num_questions": num_questions,
    "rag_output": ""  # Initialize rag_output
    }
    for output in app.stream(inputs):
        if "rag_output" in output:
            inputs["rag_output"] = output["rag_output"]
        if "mcq_json" in output:
            return json.loads(output["mcq_json"])
# Example usage
if __name__ == "__main__":
    user_input = "Basics of Digital skills"
    num_questions = 3
    result = run_graph(user_input, num_questions)
    print(json.dumps(result, indent=2))