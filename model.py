import os
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is loaded
if not api_key:
    raise ValueError("OpenAI API key not found in .env file")

# Initialize components
def initialize_chain():
    documents = []
    docs_folder = "docs"
    for filename in os.listdir(docs_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(docs_folder, filename)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load_and_split())

    # Initialize embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embedding=embeddings)
    system_prompt = (
        "You are an expert Agile coach and software process guide. Answer all questions as if you are guiding a team "
        "in Agile practices, such as Scrum and Kanban, with a focus on best practices, principles, and practical applications "
        "in software development. Your goal is to assist users in understanding and implementing Agile processes effectively. Use the context provided"
        " to provide detailed and informative responses. Avoid jargon and provide clear explanations."
    )
    # Create conversation chain with the system prompt
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini", system_prompt=system_prompt)
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