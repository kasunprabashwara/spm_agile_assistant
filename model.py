import os
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from data import get_data

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is loaded
if not api_key:
    raise ValueError("OpenAI API key not found in .env file")

# Initialize components
def initialize_chain():
    documents = get_data(docs_folder="docs")

    # Initialize embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embedding=embeddings)
    # Create conversation chain with the system prompt
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini")
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

# Initialize the chain once at startup
conversation_chain = initialize_chain()

def get_response(query: str):
    result = conversation_chain.invoke({"question": query})
    return result.get("answer", "I'm sorry, I couldn't find an answer.")