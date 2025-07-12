from dotenv import load_dotenv
import sys
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableBranch, RunnableLambda

load_dotenv()


def format_docs(docs):
    formatted_docs = []
    for doc in docs:
        verse_type = doc.metadata.get("verse_type", "Unknown")
        try:
            page_number = int(doc.metadata.get("page_number", 0))
        except (ValueError, TypeError):
            page_number = doc.metadata.get("page_number", "Unknown")

        if verse_type == "Unknown":
            header = f"Page Number: {page_number}, Verse:\n"
        else:
            header = f"Page Number: {page_number}, Verse Type: {verse_type}:\n"

        formatted_docs.append(f"{header}Content: {doc.page_content}")

    return "\n\n".join(formatted_docs)


def get_validated_response(retriever, question):
    llm = ChatOpenAI()

    llm = ChatOpenAI()
    system_prompt_text = """You are a warm, conversational spiritual guide who offers wisdom from the Ramcharitmanas. When answering questions, weave your knowledge naturally into the conversation as if sharing insights from this sacred text.
                Integrate verse references smoothly into your responses rather than using formal citations. For example, say "The Ramcharitmanas teaches us on page 715..." or "As described in the text on page 672..." instead of formal citations.
                Speak warmly and personally, as if having a meaningful conversation about spiritual matters. Avoid repetitive phrases like "based on the provided content" or parenthetical references.
                If the context doesn't address the question directly, kindly explain that this particular topic isn't covered in the sections you have access to.
                Question: {question}
                Context: {context}
                Answer:"""

    prompt = ChatPromptTemplate.from_template(system_prompt_text)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    # Format your validation prompt with question and response
    validation_prompt_text = """You are evaluating whether a response properly      answers a user's question using Ramcharitmanas content.

        A response is VALID if it:
        - Directly addresses the specific question asked
        - Contains citations to specific verses (page numbers and verse types)
        - Uses content that is actually relevant to the question topic
        - Provides spiritual guidance based on the text

        A response is INVALID if it:
        - Discusses a completely different topic than asked
        - Has no citations or verse references
        - Uses irrelevant content to answer the question

        Question: {question}
        Response: {response}

        Does this response meet the criteria for a VALID answer? Answer only yes or no.
        """
    validation_prompt = ChatPromptTemplate.from_template(validation_prompt_text)
    validation_chain = validation_prompt | llm | StrOutputParser()

    validated_chain = (
        rag_chain
        | RunnableLambda(
            lambda response: {
                "question": question,
                "response": response,
            }
        )
        | RunnableBranch(
            (
                lambda x: validation_chain.invoke(x).strip().lower() == "yes",
                lambda x: x["response"],
            ),
            lambda x: "I don't have enough information from the text to answer this question.",
        )
    )
    results = validated_chain.invoke(question)

    return results


def get_response(retriever: VectorStoreRetriever, question: str) -> str:
    llm = ChatOpenAI()
    system_prompt_text = """You are a spiritual guide who answers questions about people's problems as they relate to spirituality, using only the Ramcharitmanas document provided.First, verify that the context directly answers the specific question asked.Do not use content about one topic to answer questions about a different topic. Your response must cite specific verses from the context and explain how they relate to the user's problem. Your citation format should be 'According to [verse type] on page [number]'. Any responses without citations are unacceptable.Include relevant original Sanskrit/Devanagari text from the verses along with English translations.If the provided context doesn't contain relevant information to answer the question, say that you don't have enough information from the text.If the context discusses related but different topics, state that you don't have information about the specific question.
    Question: {question}
    Context: {context}
    Answer:"""

    prompt = ChatPromptTemplate.from_template(system_prompt_text)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    results = rag_chain.invoke(question)

    return results
