from langchain_community.vectorstores import Qdrant
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_together import ChatTogether
from langchain.chains import RetrievalQA
from qdrant_client import QdrantClient
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain



embeddings = FastEmbedEmbeddings()
url = 'https://eb73641e-e337-4ffb-aca0-cd971124d92b.europe-west3-0.gcp.cloud.qdrant.io'
api_key = '4ej2CtpmKE58hpx-JPbzF-IoUBuobQ-JBRlNI_TmdlOlu6bk48ujXw'

client = QdrantClient(url="https://eb73641e-e337-4ffb-aca0-cd971124d92b.europe-west3-0.gcp.cloud.qdrant.io", api_key = api_key)

# Initialize Qdrant as a vector store
vector_store = Qdrant(
    client=client,
    collection_name="test_rag",
    embeddings=embeddings,
)

# Initialize Together AI LLM
llm = ChatTogether(
    together_api_key="feda905a3fc3a4250e1c91e84e8639544eb02b0c9366d4d4047d3b70e69aad92",
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


result = retrieval_chain.invoke({"input": "What is digital literacy?"})
print(result['answer'])