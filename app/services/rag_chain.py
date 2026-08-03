from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.services.vectorstore import get_vectorstore

PROMPT_TEMPLATE = """You are a helpful assistant answering questions about a document.
Use ONLY the following retrieved context to answer the question.
If the answer is not contained in the context, say "I don't have enough information in the document to answer that" — do not make up an answer.

Context:
{context}

Question: {question}

Answer:"""


def _format_docs(docs) -> str:
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def answer_question(doc_id: str, question: str):
    vectorstore = get_vectorstore(doc_id)
    retriever = vectorstore.as_retriever(search_kwargs={"k": settings.TOP_K})

    retrieved_docs = retriever.invoke(question)

    if not retrieved_docs:
        return "I don't have enough information in the document to answer that.", []

    context_text = _format_docs(retrieved_docs)

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0,
    )

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context_text, "question": question})

    return answer, retrieved_docs