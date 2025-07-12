from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion import ingest
from retrievers import retrieval
from responder import response_generation

load_dotenv()

if __name__ == "__main__":
    # ingest.process_documents()
    retriever = retrieval.get_retriver()
    question = "What should a wife do?"
    response = response_generation.get_validated_response(
        retriever=retriever, question=question
    )
    print(response)
