from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
import os

load_dotenv()


def get_retriver():

    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index = pc.Index(os.environ["INDEX_NAME"])
    embeddings = OpenAIEmbeddings(
        model=os.environ["EMBEDDING_MODEL"], dimensions=os.environ["DIMENSION_SIZE"]
    )
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    retriever = vector_store.as_retriever()
    return retriever


if __name__ == "__main__":

    response = get_retriver().invoke("What is the concept of devotion")
    for item in response:
        print(f"Page Content: {item.page_content}")
        print(f"Page Content: {item.metadata}")
