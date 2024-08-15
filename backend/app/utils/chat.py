import os
from typing import Dict, Optional
from django.conf import settings

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from litellm import Router as litellmRouter
from openai import OpenAI 


from app.constants import SEMANTIC_ROUTES, DEFAULT_STRONG_MODEL_NAME, DEFAULT_WEAK_MODEL_NAME
from app.enums import OptimizationMetric, LLMName, Role
from app.utils.llmrouter import LLMRouter
from app.models import Chat
from app.utils.llms import LLMs


completion = LLMRouter.completion

# Note: This is a function, python magic 😁
get_models: Dict[str, LLMName] = lambda: {
    "strong_model_name": os.environ['STRONG_MODEL_NAME'],
    "weak_model_name": os.environ['WEAK_MODEL_NAME'],
}


def update_models(strong_model_name: LLMName = DEFAULT_STRONG_MODEL_NAME, weak_model_name: LLMName = DEFAULT_WEAK_MODEL_NAME):
    if strong_model_name not in LLMName or weak_model_name not in LLMName:
        raise ValueError("Invalid model name(s) provided")
    
    os.environ['STRONG_MODEL_NAME'] = strong_model_name
    os.environ['WEAK_MODEL_NAME'] = weak_model_name


def create_index(knowledgebase: str, chat_id: int):

    print(f"-> Creating index for chat {chat_id}", flush=True)

    # split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=200, separator=" ")
    doc = Document(page_content=knowledgebase)
    docs = text_splitter.split_documents([doc])

    # create vector db
    db = FAISS.from_documents(docs, OpenAIEmbeddings())

    # save vector db
    indexes_dir = settings.INDEXES_DIR
    if not os.path.exists(indexes_dir):
        os.makedirs(indexes_dir)
    db.save_local(os.path.join(indexes_dir, f"{chat_id}.index"))

    print(f"-> Index created for chat {chat_id}", flush=True)


def get_ai_response(query: str, chat_id: int, optimization_metric: Optional[OptimizationMetric] = None):

    print(f"-> Getting AI response for chat {chat_id}", flush=True)

    # retrieve relevant data for context
    index_path = os.path.join(settings.INDEXES_DIR, f"{chat_id}.index")
    db = FAISS.load_local(index_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    relevant_docs_and_scores = db.similarity_search_with_relevance_scores(query, k=4, score_threshold=0.6)
    context = " ".join([doc.page_content for doc, _ in relevant_docs_and_scores])
    print(f"- Retrieved context: {context}\n", flush=True)

    # get message history
    chat = Chat.objects.get(id=chat_id)
    messages = [{"role": message.role, "content": message.content} for message in chat.get_messages(k_recent=4)]
    
    # define prompt templates  
    system_message_template = """You are a helpful chatbot assistant that answers user queries from some data/knolwedgebase.\
        You will be given relevant context along with the user query; the context is the most relevant data found from the knowledgebase for the user query and it may be empty. \
        You will also receive the previous few messages in the chat history. Use the context, history, and your own intellegence to form an answer but only use the data provided, if the user's query is not clear or can't be answered with the given data/context, mention it or ask for clarification instead of making up an answer.\
        Make sure to not make the user feel like you are a human or what your underlying implementation is, for example prefer saying I dont know or I don't have that information over I cant find that information in my context.\
        
        Context:
        ```
        {context}
        ```
    """
    user_query_template = "{query}"
    
    # add system and user messages to the message history
    messages = [{"role": Role.SYSTEM.value, "content": system_message_template.format(context=context)}] \
        + messages \
        + [{"role": Role.USER.value, "content": user_query_template.format(query=query)}]

    print(f"- Final message history:\n {"\n".join([str(message) for message in messages])}\n", flush=True)

    # # override optimization metric for testing
    # optimization_metric = OptimizationMetric.LATENCY
    # get response
    # response = llm_router.completion(messages=messages, optimization_metric=optimization_metric)
    # response = completion(
    #     messages=messages,
    #     optimization_metric=optimization_metric,
    #     strong_model_name=os.environ['STRONG_MODEL_NAME'],
    #     weak_model_name=os.environ['WEAK_MODEL_NAME'],
    #     semantic_routes=SEMANTIC_ROUTES
    # )


    # make an open ai style completion request but with our own base url'
    client = OpenAI(base_url="http://localhost:8000/api/")

    # setup custom parameters
    models_info = get_models()
    strong_model = LLMs[models_info["strong_model_name"]]
    weak_model = LLMs[models_info["weak_model_name"]]
    semantics = [
        {
            "name": semantic.name,
            "model_type": semantic.llm_type,
            "utterances": semantic.utterances,
        }
        for semantic in SEMANTIC_ROUTES
    ]

    response = client.chat.completions.create(
        model="doesntmatter",
        messages=messages,
        extra_body={
            "models": {
                "strong": {
                    "model": strong_model.model,
                    "api_key": strong_model.api_key,
                    "api_base": strong_model.api_base,
                },
                "weak": {
                    "model": weak_model.model,
                    "api_key": weak_model.api_key,
                    "api_base": weak_model.api_base,
                } 
            },
            "optimization_metric": optimization_metric,
            "semantics": semantics,
        }
    )
    
    # save user message
    user_message = chat.add_message(content=query, role=Role.USER.value)

    # save ai response
    ai_message = chat.add_message(content=response.choices[0].message.content, role=Role.ASSISTANT.value,
                     model_used=response.model, metadata=response.metadata)

    # update user message metadata
    user_message.metadata = {"routing_decision": response.routing_decision}
    user_message.save()

    print(f"AI response obtained: {response.choices[0].message.content}\n", flush=True)

    return {
        "user_message": user_message.serialize(),
        "ai_message": ai_message.serialize(),
    }
