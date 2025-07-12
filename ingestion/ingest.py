from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import pprint
import re
import os
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

load_dotenv()


def doc_parser(text: str, page_number: int):
    # Find section boundaries like (1.4), (1.7), (2)
    boundary_pattern = r"\((\d+(?:\.\d+)?)\)"
    boundaries = re.findall(boundary_pattern, text)
    # print(boundaries)  # ['1.4', '1.7', '2']
    # Split text into sections
    sections = re.split(boundary_pattern, text)
    new_sections = [
        sec.strip()
        for index, sec in enumerate(sections)
        if index % 2 == 0 and sec != ""
    ]

    parsed_doc_list = []
    # Find verse numbers within sections
    for index, section in enumerate(new_sections):
        item = {
            "content": section.encode("utf-8", errors="ignore").decode("utf-8"),
            "verse_type": verse_type_finder(section),
            "page_number": page_number,
        }
        parsed_doc_list.append(item)
    return parsed_doc_list


def verse_type_finder(text: str):
    # Check for explicit verse type prefixes first
    verse_type_match = re.search(r"(Cau\.|Do\.|So\.):", text)
    if verse_type_match:
        prefix = verse_type_match.group(1)
        if prefix == "Cau.":
            return "Chaupai"
        elif prefix == "Do.":
            return "Doha"
        elif prefix == "So.":
            return "Soratha"

    # Check for Sanskrit Shloka patterns
    if re.search(r"H\s*\d+\s*H", text):
        return "Sanskrit Shloka"

    # Check for ending number pattern like (4), (5), (6)
    if re.search(r"\(\d+\)$", text.strip()):
        return "Sanskrit Shloka"

    # Default case
    return "Unknown"


def get_vector_store():
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    index_name = os.environ["INDEX_NAME"]
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    dimension_size = int(os.environ["DIMENSION_SIZE"])
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=dimension_size,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(5)
        print(f"Creating Index in Pinecone: {index_name}")

    index = pc.Index(index_name)
    embeddings = OpenAIEmbeddings(
        model=os.environ["EMBEDDING_MODEL"], dimensions=dimension_size
    )
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    return vector_store


def process_documents():
    loader = PyPDFLoader(
        "data/Sri-Ram-Charit-Manas-Hindi-Text-with-English-Translation.pdf"
    )
    docs = loader.load()

    print(f"Loaded {len(docs)} pages")

    chunked_docs = []
    # print(docs[19].page_content)
    for page_num, doc in enumerate(docs):
        chunk = doc_parser(doc.page_content, page_number=doc.metadata["page"])
        chunked_docs.extend(chunk)

    # print(f"Chunk Data: {chunked_doc[21]}")
    # langchain_docs = [
    #     Document(
    #         page_content=doc["content"],
    #         metadata={
    #             "verse_type": doc["verse_type"],
    #             "page_number": doc["page_number"],
    #         },
    #     )
    #     for doc in chunked_docs
    # ]
    ids, langchain_docs = (
        # Creating ids with {position}_{page_number} for uniqueness and the LangChain docs
        [
            f'{position}_{doc["page_number"]}'
            for position, doc in enumerate(chunked_docs)
        ],
        [
            Document(
                page_content=doc["content"],
                metadata={
                    "verse_type": doc["verse_type"],
                    "page_number": doc["page_number"],
                },
            )
            for doc in chunked_docs
        ],
    )

    store = get_vector_store()
    # Adding docs one at a time to avoid token limitation
    for index, doc in enumerate(langchain_docs):
        store.add_documents([doc], ids=[ids[index]])
        print(f"Processing document {index + 1}/{len(langchain_docs)}")


if __name__ == "__main__":
    process_documents()
