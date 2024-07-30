import os
from typing import Optional
from django.conf import settings

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from litellm import Router as litellmRouter


from app.constants import SEMANTIC_ROUTES, STRONG_MODEL_NAME, WEAK_MODEL_NAME
from app.enums import OptimizationMetric, LLMName, Role
from app.utils.llmrouter import LLMRouter
from app.models import Chat


llm_router = LLMRouter(
    strong_model_name=STRONG_MODEL_NAME,
    weak_model_name=WEAK_MODEL_NAME,
    semantic_routes=SEMANTIC_ROUTES,
)

def create_index(text: str, chat_id: int):

    # split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=200, separator=" ")
    doc = Document(page_content=text)
    docs = text_splitter.split_documents([doc])

    # create vector db
    db = FAISS.from_documents(docs, OpenAIEmbeddings())

    # save vector db
    indexes_dir = settings.INDEXES_DIR
    if not os.path.exists(indexes_dir):
        os.makedirs(indexes_dir)
    db.save_local(os.path.join(indexes_dir, f"{chat_id}.index"))


def get_ai_response(query: str, chat_id: int, index_path: str, optimization_metric: Optional[OptimizationMetric] = None):

    # retrieve relevant data
    db = FAISS.load_local(index_path)
    relevant_docs_and_scores = db.similarity_search_with_relevance_scores(query, k=4, score_threshold=0.6)
    context = " ".join([doc.page_content for doc, _ in relevant_docs_and_scores])

    # get message history
    chat = Chat.objects.get(id=chat_id)
    messages = chat.get_messages(k_recent=4)  # TODO: make k_recent configurable
    messages = [{"role": message.role, "content": message.content} for message in messages]
    
    # add system message
    system_message_content = "You are a helpful assistant that answers user queries. You will be given relevant context along with the user query, use the context and your own intellegence to form an answer but only use the data provided, if the user's query is not clear or can't be answered with the given data/context, mention instead of making up an answer."
    messages = [{"role": Role.SYSTEM.value, "content": system_message_content}] + messages

    # add new user query
    user_query_template = """Answer the given user query using the context provided, both delimited by triple backticks.
        User Query:
        ```
        {query}
        ```

        Context:
        ```
        {context}
        ```
    """
    user_query = user_query_template.format(query=query, context=context)
    messages.append({"role": "user", "content": user_query})

    # save user message
    chat.add_message(content=query, role=Role.USER.value)

    # get response
    response = llm_router.completion(messages=messages, optimization_metric=optimization_metric)

    # save ai response
    chat.add_message(content=response.choices[0].message.content, role=Role.ASSISTANT.value)
    
    return response
