from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "learning_rag"

# Vector Embeddings for each chunk
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

def index_docs(file_path: str):
    #load this file into py program
    loader = PyPDFLoader(file_path=pdf_path)
    docs = loader.load()  # returns page by page docs in an array like each page number is index of array eg. docs[3]

    # chunking the docs
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=400,   # taking little part from the previous chunk
    )

    chunks = text_splitter.split_documents(documents=docs)

    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
    )
    print("Indexing of documents done...")

    return {"message": "PDF indexed successfully"}


def ask_query(user_query:str):
    vector_db = QdrantVectorStore.from_existing_collection(
        embedding=embedding_model,
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
    )

    results = vector_db.similarity_search(query=user_query)  # relevant chunks from db

    context = "\n\n".join([
        f"Page Content: {r.page_content}\nPage Number: {r.metadata.get('page_label')}"
        for r in results
    ])

    SYSTEM_PROMPT = f"""
    You are a AI Assistant who answers user query based on the available context retrieved from the pdf file along with page_contents and page_number. 
    You should only answer the user based on the context and navigate the user to open the right page number for more information. If answer not found, say "Not found in document".

    CONTEXT:
    {context}
    """

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]
    )

    return response.choices[0].message.content